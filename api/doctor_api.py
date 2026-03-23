# ===== api/doctor_api.py =====

from common.base_api import BaseApi


class DoctorApi(BaseApi):
    """医生模块接口"""

    def get_doctor_list(self, department_id=None, hospital_id=None,
                        name="", title="", page=1, per_page=10):
        """获取医生列表"""
        params = {"page": page, "per_page": per_page}
        if department_id:
            params["department_id"] = department_id
        if hospital_id:
            params["hospital_id"] = hospital_id
        if name:
            params["name"] = name
        if title:
            params["title"] = title
        return self.get("/api/doctors", params=params)

    def get_doctor_detail(self, doctor_id):
        """获取医生详情"""
        return self.get(f"/api/doctors/{doctor_id}")