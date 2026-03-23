# ===== api/appointment_api.py =====

from common.base_api import BaseApi


class AppointmentApi(BaseApi):
    """预约挂号模块接口"""

    def create_appointment(self, schedule_id, patient_name, patient_phone,
                           patient_id_card="", remark=""):
        """
        预约挂号
        :param schedule_id: 排班ID
        :param patient_name: 就诊人姓名
        :param patient_phone: 就诊人手机号
        :param patient_id_card: 身份证号（可选）
        :param remark: 备注（可选）
        """
        data = {
            "schedule_id": schedule_id,
            "patient_name": patient_name,
            "patient_phone": patient_phone,
        }
        if patient_id_card:
            data["patient_id_card"] = patient_id_card
        if remark:
            data["remark"] = remark
        return self.post("/api/appointments", json=data)

    def get_my_appointments(self, page=1, per_page=10, status=None):
        """查看我的预约列表"""
        params = {"page": page, "per_page": per_page}
        if status is not None:
            params["status"] = status
        return self.get("/api/appointments", params=params)

    def get_appointment_detail(self, appointment_id):
        """查看预约详情"""
        return self.get(f"/api/appointments/{appointment_id}")

    def cancel_appointment(self, appointment_id, cancel_reason=""):
        """取消预约"""
        data = {}
        if cancel_reason:
            data["cancel_reason"] = cancel_reason
        return self.put(f"/api/appointments/{appointment_id}/cancel", json=data)