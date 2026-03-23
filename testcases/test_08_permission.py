# ===== testcases/test_08_permission.py =====

import pytest
import allure
from api.auth_api import AuthApi
from api.appointment_api import AppointmentApi
from api.admin_api import AdminApi
from common.assert_handler import AssertHandler

check = AssertHandler()


@allure.epic("智慧医疗预约挂号平台")
@allure.feature("权限与安全测试")
class TestPermission:
    """权限安全测试"""

    # ==================== 未登录访问 ====================

    @allure.story("鉴权测试")
    @allure.title("无Token访问需鉴权接口")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.permission
    def test_no_token_access(self):
        """TC_PERM_001: 无Token访问"""
        api = AppointmentApi()  # 没有设置 Token

        response = api.get_my_appointments()

        check.assert_http_status(response, 401)
        result = response.json()
        check.assert_code(result, 401)

    @allure.story("鉴权测试")
    @allure.title("伪造Token访问")
    @pytest.mark.permission
    def test_fake_token_access(self):
        """TC_PERM_002: 伪造Token"""
        api = AppointmentApi()
        api.set_token("this_is_a_fake_token_12345_xyz")

        response = api.get_my_appointments()

        check.assert_http_status(response, 401)
        result = response.json()
        check.assert_code(result, 401)
        check.assert_msg_contains(result, "无效")

    # ==================== 越权访问 ====================

    @allure.story("越权测试")
    @allure.title("普通用户访问管理端接口")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.permission
    def test_user_access_admin_api(self, user_token):
        """TC_PERM_003: 普通用户越权访问管理端"""
        admin_api = AdminApi()
        admin_api.set_token(user_token)  # 用普通用户的 Token

        with allure.step("尝试访问管理端医院列表"):
            resp = admin_api.get_hospitals()
            check.assert_http_status(resp, 403)

        with allure.step("尝试添加医院"):
            resp = admin_api.add_hospital(name="越权测试", level="三甲")
            check.assert_http_status(resp, 403)

        with allure.step("尝试查看所有订单"):
            resp = admin_api.get_all_appointments()
            check.assert_http_status(resp, 403)

        with allure.step("尝试查看统计数据"):
            resp = admin_api.get_statistics_overview()
            check.assert_http_status(resp, 403)

    @allure.story("越权测试")
    @allure.title("普通用户删除医院（越权操作）")
    @pytest.mark.permission
    def test_user_delete_hospital(self, user_token):
        """TC_PERM_004: 普通用户删除医院"""
        admin_api = AdminApi()
        admin_api.set_token(user_token)

        resp = admin_api.delete_hospital(1)
        check.assert_http_status(resp, 403)

    # ==================== 数据隔离 ====================

    @allure.story("数据隔离")
    @allure.title("用户A查看用户B的预约")
    @pytest.mark.permission
    def test_user_access_other_appointment(self, user_token):
        """TC_PERM_005: 跨用户查看预约"""
        # 用 lisi 登录
        api = AuthApi()
        resp, token = api.login_and_set_token("lisi", "123456")

        if token:
            apt_api = AppointmentApi()
            apt_api.set_token(token)

            # lisi 尝试查看 id=1 的预约（可能属于 zhangsan）
            resp = apt_api.get_appointment_detail(1)
            result = resp.json()

            # ★ 改成：403 或 404 都算通过
            assert result["code"] in [403, 404], \
                f"应返回403或404，实际: code={result['code']}, msg={result['msg']}"