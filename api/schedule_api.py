# ===== api/schedule_api.py =====

from common.base_api import BaseApi


class ScheduleApi(BaseApi):
    """排班模块接口"""

    def get_schedule_list(self, doctor_id=None, department_id=None,
                          start_date="", end_date=""):
        """查询排班"""
        params = {}
        if doctor_id:
            params["doctor_id"] = doctor_id
        if department_id:
            params["department_id"] = department_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.get("/api/schedules", params=params)

    def get_schedule_detail(self, schedule_id):
        """获取排班详情"""
        return self.get(f"/api/schedules/{schedule_id}")