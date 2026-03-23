# ===== testcases/test_06_appointment.py =====

import pytest
import allure
from api.appointment_api import AppointmentApi
from api.schedule_api import ScheduleApi
from common.yaml_handler import read_yaml
from common.assert_handler import AssertHandler
from common.logger_handler import logger

check = AssertHandler()


@allure.epic("智慧医疗预约挂号平台")
@allure.feature("预约挂号模块")
class TestAppointment:
    """预约挂号模块测试 - 核心业务流程"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = read_yaml("data/appointment_data.yaml")

    # ==================== 预约挂号 ====================

    @allure.story("创建预约")
    @allure.title("正常预约挂号")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.appointment
    def test_create_appointment_success(self, appointment_api, available_schedule_id,
                                         db, cleanup_test_appointment):
        """TC_APT_001: 正常预约挂号"""
        case_data = self.data["create"]["success"]

        with allure.step("记录预约前号源数"):
            schedule_before = db.query_one(
                "SELECT total_slots, booked_slots FROM schedules WHERE id = %s",
                (available_schedule_id,)
            )
            booked_before = schedule_before["booked_slots"]
            logger.info(f"预约前已预约数: {booked_before}")

        with allure.step("发送预约请求"):
            response = appointment_api.create_appointment(
                schedule_id=available_schedule_id,
                patient_name=case_data["patient_name"],
                patient_phone=case_data["patient_phone"],
                patient_id_card=case_data.get("patient_id_card", ""),
                remark=case_data.get("remark", "")
            )

        result = response.json()

        with allure.step("断言预约成功"):
            check.assert_code(result, 200)
            check.assert_msg_contains(result, "预约成功")

        with allure.step("断言返回数据完整"):
            apt_data = result["data"]
            check.assert_has_field(apt_data, "id")
            check.assert_has_field(apt_data, "order_no")
            check.assert_has_field(apt_data, "doctor_name")
            check.assert_has_field(apt_data, "hospital_name")
            check.assert_has_field(apt_data, "department_name")
            check.assert_has_field(apt_data, "appointment_date")
            check.assert_has_field(apt_data, "amount")

        with allure.step("断言状态为待就诊"):
            check.assert_equal(apt_data["status"], 0, "预约状态")
            check.assert_equal(apt_data["status_text"], "待就诊", "状态文本")

        with allure.step("断言患者信息正确"):
            check.assert_equal(apt_data["patient_name"], case_data["patient_name"], "患者姓名")
            check.assert_equal(apt_data["patient_phone"], case_data["patient_phone"], "患者手机号")

        with allure.step("断言挂号费大于0"):
            check.assert_greater_than(apt_data["amount"], 0, "挂号费")

        with allure.step("断言订单号格式正确"):
            order_no = apt_data["order_no"]
            assert order_no.startswith("APT"), f"订单号应以APT开头: {order_no}"
            assert len(order_no) == 23, f"订单号长度应为23: {len(order_no)}"

        with allure.step("数据库验证-预约记录"):
            db_apt = check.assert_db_exists(
                db,
                "SELECT * FROM appointments WHERE id = %s",
                (apt_data["id"],),
                msg="预约记录"
            )
            check.assert_equal(db_apt["patient_name"], case_data["patient_name"], "DB患者姓名")
            check.assert_equal(db_apt["status"], 0, "DB预约状态")

        with allure.step("数据库验证-号源已扣减"):
            schedule_after = db.query_one(
                "SELECT booked_slots FROM schedules WHERE id = %s",
                (available_schedule_id,)
            )
            check.assert_equal(
                schedule_after["booked_slots"],
                booked_before + 1,
                "已预约数应+1"
            )

        # 记录ID用于清理
        cleanup_test_appointment.append(apt_data["id"])

    @allure.story("创建预约")
    @allure.title("重复预约同一排班")
    @pytest.mark.appointment
    def test_create_appointment_duplicate(self, appointment_api, available_schedule_id,
                                           cleanup_test_appointment):
        """TC_APT_002: 重复预约"""
        # 先预约一次
        response1 = appointment_api.create_appointment(
            schedule_id=available_schedule_id,
            patient_name="重复测试",
            patient_phone="13800138001"
        )
        result1 = response1.json()

        if result1["code"] == 200:
            cleanup_test_appointment.append(result1["data"]["id"])

            with allure.step("再次预约同一排班"):
                response2 = appointment_api.create_appointment(
                    schedule_id=available_schedule_id,
                    patient_name="重复测试",
                    patient_phone="13800138001"
                )
                result2 = response2.json()

            with allure.step("断言重复预约失败"):
                check.assert_code(result2, 400)
                check.assert_msg_contains(result2, "已预约")

    @allure.story("创建预约")
    @allure.title("预约-就诊人姓名为空")
    @pytest.mark.appointment
    def test_create_appointment_empty_name(self, appointment_api, available_schedule_id):
        """TC_APT_003: 就诊人姓名为空"""
        case_data = self.data["create"]["empty_patient_name"]

        response = appointment_api.create_appointment(
            schedule_id=available_schedule_id,
            patient_name=case_data["patient_name"],
            patient_phone=case_data["patient_phone"]
        )
        result = response.json()

        check.assert_code(result, case_data["expected_code"])
        check.assert_msg_contains(result, case_data["expected_msg"])

    @allure.story("创建预约")
    @allure.title("预约-排班ID不存在")
    @pytest.mark.appointment
    def test_create_appointment_invalid_schedule(self, appointment_api):
        """TC_APT_004: 排班不存在"""
        response = appointment_api.create_appointment(
            schedule_id=99999,
            patient_name="测试",
            patient_phone="13800138001"
        )
        result = response.json()

        check.assert_code(result, 404)
        check.assert_msg_contains(result, "不存在")

    # ==================== 查看预约 ====================

    @allure.story("查看预约")
    @allure.title("查看我的预约列表")
    @pytest.mark.smoke
    @pytest.mark.appointment
    def test_get_my_appointments(self, appointment_api):
        """TC_APT_005: 查看预约列表"""
        response = appointment_api.get_my_appointments()
        result = response.json()

        check.assert_code(result, 200)
        check.assert_has_field(result["data"], "list")
        check.assert_has_field(result["data"], "total")

    @allure.story("查看预约")
    @allure.title("按状态筛选预约")
    @pytest.mark.appointment
    def test_get_appointments_by_status(self, appointment_api):
        """TC_APT_006: 按状态筛选"""
        response = appointment_api.get_my_appointments(status=0)
        result = response.json()

        check.assert_code(result, 200)

        # 如果有数据，验证状态都是待就诊
        for apt in result["data"]["list"]:
            check.assert_equal(apt["status"], 0, "预约状态")

    # ==================== 取消预约 ====================

    @allure.story("取消预约")
    @allure.title("正常取消预约")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.appointment
    def test_cancel_appointment(self, appointment_api, available_schedule_id, db):
        """TC_APT_007: 正常取消"""
        # 先创建一个预约
        with allure.step("先创建一个预约"):
            create_resp = appointment_api.create_appointment(
                schedule_id=available_schedule_id,
                patient_name="取消测试用户",
                patient_phone="13800130099"
            )
            create_result = create_resp.json()

            if create_result["code"] != 200:
                pytest.skip("创建预约失败，跳过取消测试")

            appointment_id = create_result["data"]["id"]
            logger.info(f"创建预约成功: id={appointment_id}")

        with allure.step("记录取消前号源"):
            schedule_before = db.query_one(
                "SELECT booked_slots FROM schedules WHERE id = %s",
                (available_schedule_id,)
            )
            booked_before = schedule_before["booked_slots"]

        with allure.step("发送取消请求"):
            cancel_resp = appointment_api.cancel_appointment(
                appointment_id,
                cancel_reason="自动化测试取消"
            )
            cancel_result = cancel_resp.json()

        with allure.step("断言取消成功"):
            check.assert_code(cancel_result, 200)
            check.assert_msg_contains(cancel_result, "取消成功")

        with allure.step("数据库验证-状态变为已取消"):
            db_apt = db.query_one(
                "SELECT status, cancel_reason FROM appointments WHERE id = %s",
                (appointment_id,)
            )
            check.assert_equal(db_apt["status"], 2, "取消后状态")
            check.assert_equal(db_apt["cancel_reason"], "自动化测试取消", "取消原因")

        with allure.step("数据库验证-号源已释放"):
            schedule_after = db.query_one(
                "SELECT booked_slots FROM schedules WHERE id = %s",
                (available_schedule_id,)
            )
            check.assert_equal(
                schedule_after["booked_slots"],
                booked_before - 1,
                "号源应释放(-1)"
            )

    @allure.story("取消预约")
    @allure.title("重复取消已取消的预约")
    @pytest.mark.appointment
    def test_cancel_already_cancelled(self, appointment_api, available_schedule_id):
        """TC_APT_008: 重复取消"""
        # 先创建再取消
        create_resp = appointment_api.create_appointment(
            schedule_id=available_schedule_id,
            patient_name="重复取消测试",
            patient_phone="13800130088"
        )
        create_result = create_resp.json()

        if create_result["code"] != 200:
            pytest.skip("创建预约失败")

        appointment_id = create_result["data"]["id"]

        # 第一次取消
        appointment_api.cancel_appointment(appointment_id, cancel_reason="第一次取消")

        with allure.step("再次取消（应失败）"):
            resp2 = appointment_api.cancel_appointment(appointment_id, cancel_reason="第二次取消")
            result2 = resp2.json()

        check.assert_code(result2, 400)
        check.assert_msg_contains(result2, "已取消")