# ===== conftest.py =====

import pytest
from datetime import date, timedelta
from api.auth_api import AuthApi
from api.hospital_api import HospitalApi
from api.department_api import DepartmentApi
from api.doctor_api import DoctorApi
from api.schedule_api import ScheduleApi
from api.appointment_api import AppointmentApi
from api.admin_api import AdminApi
from common.db_handler import DBHandler
from common.yaml_handler import read_config
from common.logger_handler import logger


# ==================== 全局配置 ====================

@pytest.fixture(scope="session", autouse=True)
def session_start():
    """整个测试会话开始时执行"""
    logger.info("=" * 80)
    logger.info("🚀 接口自动化测试开始")
    logger.info("=" * 80)
    yield
    logger.info("=" * 80)
    logger.info("🏁 接口自动化测试结束")
    logger.info("=" * 80)


# ==================== 数据库 ====================

@pytest.fixture(scope="session")
def db():
    """数据库连接（整个会话共享）"""
    db = DBHandler()
    yield db
    db.close()


# ==================== Token / 登录态 ====================

@pytest.fixture(scope="session")
def user_token():
    """获取普通用户 Token（整个会话只登录一次）"""
    config = read_config()
    api = AuthApi()
    response, token = api.login_and_set_token(
        config["test_user"]["username"],
        config["test_user"]["password"]
    )
    assert token is not None, "用户登录失败，无法获取 Token"
    logger.info(f"普通用户 Token 获取成功")
    return token


@pytest.fixture(scope="session")
def admin_token():
    """获取管理员 Token（整个会话只登录一次）"""
    config = read_config()
    api = AdminApi()
    response, token = api.login_and_set_token(
        config["admin_user"]["username"],
        config["admin_user"]["password"]
    )
    assert token is not None, "管理员登录失败，无法获取 Token"
    logger.info(f"管理员 Token 获取成功")
    return token


# ==================== 接口实例（已登录） ====================

@pytest.fixture(scope="class")
def auth_api():
    """认证接口实例（无 Token）"""
    return AuthApi()


@pytest.fixture(scope="class")
def user_auth_api(user_token):
    """认证接口实例（已登录）"""
    api = AuthApi()
    api.set_token(user_token)
    return api


@pytest.fixture(scope="class")
def hospital_api():
    """医院接口实例（不需要登录）"""
    return HospitalApi()


@pytest.fixture(scope="class")
def department_api():
    """科室接口实例"""
    return DepartmentApi()


@pytest.fixture(scope="class")
def doctor_api():
    """医生接口实例"""
    return DoctorApi()


@pytest.fixture(scope="class")
def schedule_api():
    """排班接口实例"""
    return ScheduleApi()


@pytest.fixture(scope="class")
def appointment_api(user_token):
    """预约接口实例（已登录）"""
    api = AppointmentApi()
    api.set_token(user_token)
    return api


@pytest.fixture(scope="class")
def admin_api(admin_token):
    """管理端接口实例（管理员已登录）"""
    api = AdminApi()
    api.set_token(admin_token)
    return api


# ==================== 公共数据 ====================

@pytest.fixture(scope="session")
def future_date():
    """生成未来的日期（用于排班测试）"""
    return (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")


@pytest.fixture(scope="session")
def available_schedule_id(user_token):
    """获取一个有号源的排班ID（必须是明天及以后，这样才能取消）"""
    from datetime import date, timedelta
    tomorrow = date.today() + timedelta(days=1)

    api = ScheduleApi()
    api.set_token(user_token)
    response = api.get_schedule_list(doctor_id=1)
    schedules = response.json().get("data", [])

    for s in schedules:
        # ★ 必须是明天及以后 + 有号源
        if s["available_slots"] > 0 and s["work_date"] > tomorrow.strftime("%Y-%m-%d"):
            logger.info(f"找到可用排班: id={s['id']}, 日期={s['work_date']}, 剩余={s['available_slots']}")
            return s["id"]

    pytest.skip("没有可用的未来排班，跳过需要排班的测试")


# ==================== 数据清理 ====================

@pytest.fixture()
def cleanup_test_user(db):
    """测试后清理自动化创建的用户"""
    yield
    db.execute(
        "DELETE FROM users WHERE username LIKE %s",
        ("auto_test_%",)
    )
    logger.info("已清理测试用户数据")


@pytest.fixture()
def cleanup_test_appointment(db):
    """测试后清理预约数据"""
    created_ids = []
    yield created_ids
    for apt_id in created_ids:
        # 先恢复号源
        db.execute("""
            UPDATE schedules s 
            JOIN appointments a ON s.id = a.schedule_id 
            SET s.booked_slots = s.booked_slots - 1 
            WHERE a.id = %s AND a.status = 0
        """, (apt_id,))
        # 删除预约
        db.execute("DELETE FROM appointments WHERE id = %s", (apt_id,))
    logger.info(f"已清理测试预约数据: {created_ids}")