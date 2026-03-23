# ===== testcases/test_07_admin.py =====

import pytest
import allure
from datetime import date, timedelta
from common.yaml_handler import read_yaml
from common.assert_handler import AssertHandler
from common.logger_handler import logger

check = AssertHandler()


@allure.epic("智慧医疗预约挂号平台")
@allure.feature("管理端")
class TestAdmin:
    """管理端测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = read_yaml("data/admin_data.yaml")

    # ==================== 医院CRUD ====================

    @allure.story("医院管理")
    @allure.title("添加→修改→删除 医院（全流程）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.admin
    def test_hospital_crud(self, admin_api, db):
        """TC_ADMIN_001: 医院增删改全流程"""
        hospital_data = self.data["hospital"]["add_success"]

        # --- 添加 ---
        with allure.step("添加医院"):
            resp = admin_api.add_hospital(
                name=hospital_data["name"],
                level=hospital_data["level"],
                address=hospital_data["address"],
                phone=hospital_data["phone"],
                description=hospital_data["description"]
            )
            result = resp.json()

            check.assert_code(result, 200)
            check.assert_msg_contains(result, "添加成功")
            hospital_id = result["data"]["id"]
            check.assert_equal(result["data"]["name"], hospital_data["name"], "医院名称")
            logger.info(f"添加医院成功: id={hospital_id}")

        with allure.step("数据库验证已添加"):
            check.assert_db_exists(
                db,
                "SELECT * FROM hospitals WHERE id = %s",
                (hospital_id,),
                msg="新增医院"
            )

        # --- 修改 ---
        with allure.step("修改医院名称"):
            resp = admin_api.update_hospital(hospital_id, name="修改后的医院名称")
            result = resp.json()

            check.assert_code(result, 200)
            check.assert_equal(result["data"]["name"], "修改后的医院名称", "修改后名称")

        with allure.step("数据库验证已修改"):
            db_hospital = db.query_one(
                "SELECT name FROM hospitals WHERE id = %s",
                (hospital_id,)
            )
            check.assert_equal(db_hospital["name"], "修改后的医院名称", "DB医院名称")

        # --- 删除 ---
        with allure.step("删除医院"):
            resp = admin_api.delete_hospital(hospital_id)
            result = resp.json()

            check.assert_code(result, 200)
            check.assert_msg_contains(result, "删除成功")

        with allure.step("数据库验证已删除"):
            check.assert_db_not_exists(
                db,
                "SELECT * FROM hospitals WHERE id = %s",
                (hospital_id,),
                msg="已删除医院"
            )

    @allure.story("医院管理")
    @allure.title("添加医院-名称为空")
    @pytest.mark.admin
    def test_add_hospital_empty_name(self, admin_api):
        """TC_ADMIN_002: 添加医院名称为空"""
        data = self.data["hospital"]["add_empty_name"]

        resp = admin_api.add_hospital(name=data["name"], level=data["level"])
        result = resp.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("医院管理")
    @allure.title("添加医院-名称重复")
    @pytest.mark.admin
    def test_add_hospital_duplicate(self, admin_api):
        """TC_ADMIN_003: 添加重复医院"""
        data = self.data["hospital"]["add_duplicate_name"]

        resp = admin_api.add_hospital(name=data["name"], level=data["level"])
        result = resp.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    # ==================== 完整CRUD链路 ====================

    @allure.story("全链路")
    @allure.title("管理端完整链路：建医院→建科室→建医生→建排班→删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.admin
    def test_admin_full_chain(self, admin_api, db):
        """TC_ADMIN_004: 管理端完整操作链路"""
        dept_data = self.data["department"]["add_success"]
        doc_data = self.data["doctor"]["add_success"]
        sch_data = self.data["schedule"]["add_success"]

        future = (date.today() + timedelta(days=8)).strftime("%Y-%m-%d")

        # 1. 添加医院
        with allure.step("1.添加医院"):
            resp = admin_api.add_hospital(name="链路测试医院", level="二乙", address="测试地址")
            hospital_id = resp.json()["data"]["id"]
            logger.info(f"创建医院: id={hospital_id}")

        # 2. 添加科室
        with allure.step("2.添加科室"):
            resp = admin_api.add_department(
                hospital_id=hospital_id,
                name=dept_data["name"],
                description=dept_data["description"]
            )
            dept_id = resp.json()["data"]["id"]
            logger.info(f"创建科室: id={dept_id}")

        # 3. 添加医生
        with allure.step("3.添加医生"):
            resp = admin_api.add_doctor(
                department_id=dept_id,
                name=doc_data["name"],
                title=doc_data["title"],
                specialty=doc_data["specialty"],
                consultation_fee=doc_data["consultation_fee"]
            )
            doctor_id = resp.json()["data"]["id"]
            logger.info(f"创建医生: id={doctor_id}")

        # 4. 添加排班
        with allure.step("4.添加排班"):
            resp = admin_api.add_schedule(
                doctor_id=doctor_id,
                work_date=future,
                time_period=sch_data["time_period"],
                total_slots=sch_data["total_slots"],
                start_time=sch_data["start_time"],
                end_time=sch_data["end_time"]
            )
            result = resp.json()
            check.assert_code(result, 200)
            schedule_id = result["data"]["id"]
            logger.info(f"创建排班: id={schedule_id}")

            check.assert_equal(result["data"]["total_slots"], sch_data["total_slots"], "号源数")
            check.assert_equal(result["data"]["available_slots"], sch_data["total_slots"], "剩余号源")

        # 5. 数据库验证完整链路
        with allure.step("5.数据库验证完整链路"):
            db_schedule = db.query_one("""
                SELECT s.*, d.name as doctor_name, dep.name as dept_name, h.name as hospital_name
                FROM schedules s
                JOIN doctors d ON s.doctor_id = d.id
                JOIN departments dep ON d.department_id = dep.id
                JOIN hospitals h ON dep.hospital_id = h.id
                WHERE s.id = %s
            """, (schedule_id,))

            check.assert_equal(db_schedule["doctor_name"], doc_data["name"], "DB医生")
            check.assert_equal(db_schedule["dept_name"], dept_data["name"], "DB科室")
            check.assert_equal(db_schedule["hospital_name"], "链路测试医院", "DB医院")

        # 6. 清理：反向删除
        with allure.step("6.清理测试数据"):
            admin_api.delete_schedule(schedule_id)
            admin_api.delete_doctor(doctor_id)
            admin_api.delete_department(dept_id)
            admin_api.delete_hospital(hospital_id)
            logger.info("测试数据清理完成")

    # ==================== 统计 ====================

    @allure.story("数据统计")
    @allure.title("查看统计概览")
    @pytest.mark.smoke
    @pytest.mark.admin
    def test_statistics_overview(self, admin_api):
        """TC_ADMIN_005: 统计概览"""
        resp = admin_api.get_statistics_overview()
        result = resp.json()

        check.assert_code(result, 200)

        data = result["data"]
        for field in ["total_appointments", "total_users", "total_doctors", "total_hospitals"]:
            check.assert_has_field(data, field)

        check.assert_greater_than(data["total_hospitals"], 0, "医院总数")
        check.assert_greater_than(data["total_doctors"], 0, "医生总数")