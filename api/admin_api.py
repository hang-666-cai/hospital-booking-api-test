# ===== api/admin_api.py =====

from common.base_api import BaseApi


class AdminApi(BaseApi):
    """管理端接口"""

    # ========== 登录 ==========
    def login(self, username, password):
        """管理员登录"""
        return self.post("/api/admin/login", json={
            "username": username,
            "password": password
        })

    def login_and_set_token(self, username, password):
        """登录并设置 Token"""
        response = self.login(username, password)
        result = response.json()
        if result.get("code") == 200:
            token = result["data"]["token"]
            self.set_token(token)
            return response, token
        return response, None

    # ========== 医院管理 ==========
    def add_hospital(self, name, level="", address="", phone="", description=""):
        """添加医院"""
        data = {
            "name": name,
            "level": level,
            "address": address,
            "phone": phone,
            "description": description
        }
        return self.post("/api/admin/hospitals", json=data)

    def update_hospital(self, hospital_id, **kwargs):
        """修改医院"""
        return self.put(f"/api/admin/hospitals/{hospital_id}", json=kwargs)

    def delete_hospital(self, hospital_id):
        """删除医院"""
        return self.delete(f"/api/admin/hospitals/{hospital_id}")

    def get_hospitals(self, page=1, per_page=10, name=""):
        """查询医院列表（管理端）"""
        params = {"page": page, "per_page": per_page}
        if name:
            params["name"] = name
        return self.get("/api/admin/hospitals", params=params)

    # ========== 科室管理 ==========
    def add_department(self, hospital_id, name, description="", sort_order=0):
        """添加科室"""
        return self.post("/api/admin/departments", json={
            "hospital_id": hospital_id,
            "name": name,
            "description": description,
            "sort_order": sort_order
        })

    def delete_department(self, dept_id):
        """删除科室"""
        return self.delete(f"/api/admin/departments/{dept_id}")

    # ========== 医生管理 ==========
    def add_doctor(self, department_id, name, title="", specialty="", consultation_fee=0):
        """添加医生"""
        return self.post("/api/admin/doctors", json={
            "department_id": department_id,
            "name": name,
            "title": title,
            "specialty": specialty,
            "consultation_fee": consultation_fee
        })

    def delete_doctor(self, doctor_id):
        """删除医生"""
        return self.delete(f"/api/admin/doctors/{doctor_id}")

    # ========== 排班管理 ==========
    def add_schedule(self, doctor_id, work_date, time_period, total_slots=10,
                     start_time="", end_time=""):
        """添加排班"""
        data = {
            "doctor_id": doctor_id,
            "work_date": work_date,
            "time_period": time_period,
            "total_slots": total_slots
        }
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
        return self.post("/api/admin/schedules", json=data)

    def update_schedule(self, schedule_id, **kwargs):
        """修改排班"""
        return self.put(f"/api/admin/schedules/{schedule_id}", json=kwargs)

    def delete_schedule(self, schedule_id):
        """删除排班"""
        return self.delete(f"/api/admin/schedules/{schedule_id}")

    # ========== 订单管理 ==========
    def get_all_appointments(self, page=1, per_page=10, **kwargs):
        """查看所有订单"""
        params = {"page": page, "per_page": per_page, **kwargs}
        return self.get("/api/admin/appointments", params=params)

    def update_appointment_status(self, appointment_id, status, cancel_reason=""):
        """修改订单状态"""
        data = {"status": status}
        if cancel_reason:
            data["cancel_reason"] = cancel_reason
        return self.put(f"/api/admin/appointments/{appointment_id}/status", json=data)

    # ========== 用户管理 ==========
    def get_users(self, page=1, per_page=10, **kwargs):
        """查看用户列表"""
        params = {"page": page, "per_page": per_page, **kwargs}
        return self.get("/api/admin/users", params=params)

    def update_user_status(self, user_id, status):
        """启用/禁用用户"""
        return self.put(f"/api/admin/users/{user_id}/status", json={"status": status})

    # ========== 统计 ==========
    def get_statistics_overview(self):
        """数据统计概览"""
        return self.get("/api/admin/statistics/overview")

    def get_statistics_daily(self, days=7):
        """每日统计"""
        return self.get("/api/admin/statistics/daily", params={"days": days})