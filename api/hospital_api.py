# ===== api/hospital_api.py =====

from common.base_api import BaseApi


class HospitalApi(BaseApi):
    """医院模块接口"""

    def get_hospital_list(self, page=1, per_page=10, name="", level=""):
        """获取医院列表"""
        params = {"page": page, "per_page": per_page}
        if name:
            params["name"] = name
        if level:
            params["level"] = level
        return self.get("/api/hospitals", params=params)

    def get_hospital_detail(self, hospital_id):
        """获取医院详情"""
        return self.get(f"/api/hospitals/{hospital_id}")