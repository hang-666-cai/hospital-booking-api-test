# ===== api/department_api.py =====

from common.base_api import BaseApi


class DepartmentApi(BaseApi):
    """科室模块接口"""

    def get_department_list(self, hospital_id):
        """获取科室列表"""
        return self.get("/api/departments", params={"hospital_id": hospital_id})

    def get_department_detail(self, dept_id):
        """获取科室详情（含医生列表）"""
        return self.get(f"/api/departments/{dept_id}")