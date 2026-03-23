# ===== testcases/test_01_auth.py =====

import pytest
import allure
from api.auth_api import AuthApi
from common.yaml_handler import read_yaml
from common.assert_handler import AssertHandler

check = AssertHandler()


@allure.epic("智慧医疗预约挂号平台")
@allure.feature("用户认证模块")
class TestAuth:
    """用户认证模块测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试类初始化"""
        self.api = AuthApi()
        self.data = read_yaml("data/auth_data.yaml")

    # ==================== 注册 ====================

    @allure.story("用户注册")
    @allure.title("正常注册新用户")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_register_success(self, cleanup_test_user, db):
        """TC_AUTH_001: 正常注册"""
        data = self.data["register"]["success"]

        with allure.step("发送注册请求"):
            response = self.api.register(
                username=data["username"],
                password=data["password"],
                phone=data["phone"],
                real_name=data["real_name"]
            )

        result = response.json()

        with allure.step("断言业务状态码为200"):
            check.assert_code(result, 200)

        with allure.step("断言返回user_id"):
            check.assert_has_field(result["data"], "user_id")
            check.assert_greater_than(result["data"]["user_id"], 0, "user_id")

        with allure.step("断言提示注册成功"):
            check.assert_msg_contains(result, "注册成功")

        with allure.step("数据库验证用户已创建"):
            db_user = check.assert_db_exists(
                db,
                "SELECT * FROM users WHERE username = %s",
                (data["username"],),
                msg="注册用户"
            )
            check.assert_equal(db_user["phone"], data["phone"], "手机号")
            check.assert_equal(db_user["real_name"], data["real_name"], "姓名")
            check.assert_equal(db_user["role"], "user", "角色")

    @allure.story("用户注册")
    @allure.title("注册-用户名为空")
    @pytest.mark.auth
    def test_register_empty_username(self):
        """TC_AUTH_002: 用户名为空"""
        data = self.data["register"]["empty_username"]

        response = self.api.register(
            username=data["username"],
            password=data["password"],
            phone=data["phone"]
        )
        result = response.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("用户注册")
    @allure.title("注册-密码太短")
    @pytest.mark.auth
    def test_register_short_password(self):
        """TC_AUTH_003: 密码太短"""
        data = self.data["register"]["short_password"]

        response = self.api.register(
            username=data["username"],
            password=data["password"],
            phone=data["phone"]
        )
        result = response.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("用户注册")
    @allure.title("注册-手机号格式错误")
    @pytest.mark.auth
    def test_register_invalid_phone(self):
        """TC_AUTH_004: 手机号格式错误"""
        data = self.data["register"]["invalid_phone"]

        response = self.api.register(
            username=data["username"],
            password=data["password"],
            phone=data["phone"]
        )
        result = response.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("用户注册")
    @allure.title("注册-用户名已存在")
    @pytest.mark.auth
    def test_register_duplicate_username(self):
        """TC_AUTH_005: 用户名已存在"""
        data = self.data["register"]["duplicate_username"]

        response = self.api.register(
            username=data["username"],
            password=data["password"],
            phone=data["phone"]
        )
        result = response.json()

        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    # ==================== 登录 ====================

    @allure.story("用户登录")
    @allure.title("正常登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_login_success(self):
        """TC_AUTH_006: 正常登录"""
        data = self.data["login"]["success"]

        with allure.step("发送登录请求"):
            response = self.api.login(data["username"], data["password"])

        result = response.json()

        with allure.step("断言登录成功"):
            check.assert_code(result, 200)
            check.assert_has_field(result["data"], "token")
            check.assert_has_field(result["data"], "user")

        with allure.step("断言Token不为空"):
            token = result["data"]["token"]
            assert len(token) > 10, f"Token长度异常: {len(token)}"

        with allure.step("断言用户信息正确"):
            user = result["data"]["user"]
            check.assert_equal(user["username"], data["username"], "用户名")
            check.assert_equal(user["role"], "user", "角色")
            check.assert_equal(user["status"], 1, "状态")
            assert "password" not in user, "响应不应包含密码字段"

    @allure.story("用户登录")
    @allure.title("登录-密码错误")
    @pytest.mark.auth
    def test_login_wrong_password(self):
        """TC_AUTH_007: 密码错误"""
        data = self.data["login"]["wrong_password"]

        response = self.api.login(data["username"], data["password"])
        result = response.json()


        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("用户登录")
    @allure.title("登录-用户不存在")
    @pytest.mark.auth
    def test_login_user_not_found(self):
        """TC_AUTH_008: 用户不存在"""
        data = self.data["login"]["user_not_found"]

        response = self.api.login(data["username"], data["password"])
        result = response.json()


        check.assert_code(result, data["expected_code"])
        check.assert_msg_contains(result, data["expected_msg"])

    @allure.story("用户登录")
    @allure.title("参数化登录测试")
    @pytest.mark.auth
    @pytest.mark.parametrize("case_data", read_yaml("data/auth_data.yaml")["login_parametrize"],
                             ids=[c["case_title"] for c in read_yaml("data/auth_data.yaml")["login_parametrize"]])
    def test_login_parametrize(self, case_data):
        """TC_AUTH_009-013: 登录参数化测试"""
        allure.dynamic.title(f"参数化登录-{case_data['case_title']}")

        response = self.api.login(case_data["username"], case_data["password"])
        result = response.json()

        check.assert_code(result, case_data["expected_code"])

    # ==================== 个人信息 ====================

    @allure.story("个人信息")
    @allure.title("获取个人信息")
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_get_profile(self, user_auth_api):
        """TC_AUTH_014: 获取个人信息"""
        response = user_auth_api.get_profile()
        result = response.json()

        check.assert_code(result, 200)
        check.assert_has_field(result["data"], "username")
        check.assert_has_field(result["data"], "phone")
        check.assert_has_field(result["data"], "real_name")
        assert "password" not in result["data"], "不应返回密码"
        assert "password_hash" not in result["data"], "不应返回密码哈希"

    @allure.story("个人信息")
    @allure.title("修改个人信息")
    @pytest.mark.auth
    def test_update_profile(self, user_auth_api):
        """TC_AUTH_015: 修改个人信息"""
        response = user_auth_api.update_profile(
            real_name="自动化修改姓名",
            gender=1
        )
        result = response.json()

        check.assert_code(result, 200)
        check.assert_equal(result["data"]["real_name"], "自动化修改姓名", "修改后姓名")
        check.assert_equal(result["data"]["gender"], 1, "修改后性别")

        # 改回去
        user_auth_api.update_profile(real_name="张三", gender=1)