# ===== testcases/test_02_hospital.py =====

import pytest
import allure
from common.yaml_handler import read_yaml
from common.assert_handler import AssertHandler

check = AssertHandler()


@allure.epic("智慧医疗预约挂号平台")
@allure.feature("医院模块")
class TestHospital:
    """医院模块测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = read_yaml("data/hospital_data.yaml")

    @allure.story("医院列表")
    @allure.title("查看医院列表-默认")
    @pytest.mark.smoke
    @pytest.mark.hospital
    def test_hospital_list(self, hospital_api):
        """TC_HOSP_001: 查看医院列表"""
        response = hospital_api.get_hospital_list()
        result = response.json()

        with allure.step("断言返回成功"):
            check.assert_code(result, 200)

        with allure.step("断言列表不为空"):
            check.assert_has_field(result["data"], "list")
            check.assert_has_field(result["data"], "total")
            check.assert_list_not_empty(result["data"]["list"], "医院列表")
            check.assert_greater_than(result["data"]["total"], 0, "total")

        with allure.step("断言数据字段完整"):
            hospital = result["data"]["list"][0]
            for field in ["id", "name", "level", "address", "phone", "status"]:
                check.assert_has_field(hospital, field)

    @allure.story("医院搜索")
    @allure.title("按名称搜索医院")
    @pytest.mark.hospital
    def test_search_hospital_by_name(self, hospital_api):
        """TC_HOSP_002: 按名称搜索"""
        search_data = self.data["search"]["by_name"]

        response = hospital_api.get_hospital_list(name=search_data["name"])
        result = response.json()

        check.assert_code(result, 200)
        check.assert_greater_than(
            result["data"]["total"],
            search_data["expected_min_count"] - 1,
            "搜索结果数量"
        )

        # 验证搜索结果都包含关键词
        for hospital in result["data"]["list"]:
            assert search_data["name"] in hospital["name"], \
                f"搜索结果'{hospital['name']}'不包含关键词'{search_data['name']}'"

    @allure.story("医院搜索")
    @allure.title("按等级筛选医院")
    @pytest.mark.hospital
    def test_search_hospital_by_level(self, hospital_api):
        """TC_HOSP_003: 按等级筛选"""
        search_data = self.data["search"]["by_level"]

        response = hospital_api.get_hospital_list(level=search_data["level"])
        result = response.json()

        check.assert_code(result, 200)

        for hospital in result["data"]["list"]:
            check.assert_equal(hospital["level"], search_data["level"], "医院等级")

    @allure.story("医院搜索")
    @allure.title("搜索不存在的医院")
    @pytest.mark.hospital
    def test_search_hospital_not_found(self, hospital_api):
        """TC_HOSP_004: 搜索不存在的医院"""
        search_data = self.data["search"]["not_found"]

        response = hospital_api.get_hospital_list(name=search_data["name"])
        result = response.json()

        check.assert_code(result, 200)
        check.assert_equal(result["data"]["total"], 0, "搜索结果数量")

    @allure.story("医院详情")
    @allure.title("查看医院详情")
    @pytest.mark.smoke
    @pytest.mark.hospital
    def test_hospital_detail(self, hospital_api):
        """TC_HOSP_005: 查看医院详情"""
        response = hospital_api.get_hospital_detail(1)
        result = response.json()

        check.assert_code(result, 200)
        check.assert_has_field(result["data"], "name")
        check.assert_has_field(result["data"], "departments")
        check.assert_list_not_empty(result["data"]["departments"], "科室列表")

    @allure.story("医院详情")
    @allure.title("查看不存在的医院")
    @pytest.mark.hospital
    def test_hospital_detail_not_found(self, hospital_api):
        """TC_HOSP_006: 不存在的医院"""
        response = hospital_api.get_hospital_detail(99999)
        result = response.json()

        check.assert_code(result, 404)
        check.assert_msg_contains(result, "不存在")

    @allure.story("分页")
    @allure.title("分页查询验证")
    @pytest.mark.hospital
    def test_hospital_list_pagination(self, hospital_api):
        """TC_HOSP_007: 分页测试"""
        response = hospital_api.get_hospital_list(page=1, per_page=2)
        result = response.json()

        check.assert_code(result, 200)
        assert len(result["data"]["list"]) <= 2, "每页数量应不超过2"
        check.assert_has_field(result["data"], "pages")