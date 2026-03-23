# ===== api/auth_api.py =====

from common.base_api import BaseApi


class AuthApi(BaseApi):
    """认证模块接口"""

    def register(self, username, password, phone, real_name=""):
        """用户注册"""
        data = {
            "username": username,
            "password": password,
            "phone": phone,
            "real_name": real_name
        }
        return self.post("/api/auth/register", json=data)

    def login(self, username, password):
        """用户登录"""
        data = {
            "username": username,
            "password": password
        }
        return self.post("/api/auth/login", json=data)

    def get_profile(self):
        """获取个人信息"""
        return self.get("/api/auth/profile")

    def update_profile(self, **kwargs):
        """
        修改个人信息
        可传参数: real_name, phone, id_card, gender
        """
        return self.put("/api/auth/profile", json=kwargs)

    def change_password(self, old_password, new_password):
        """修改密码"""
        data = {
            "old_password": old_password,
            "new_password": new_password
        }
        return self.put("/api/auth/change-password", json=data)

    def login_and_set_token(self, username, password):
        """
        登录并自动设置 Token（便捷方法）
        :return: (response, token)
        """
        response = self.login(username, password)
        result = response.json()
        if result.get("code") == 200:
            token = result["data"]["token"]
            self.set_token(token)
            return response, token
        return response, None