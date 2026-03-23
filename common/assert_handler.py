# ===== common/assert_handler.py =====

from common.logger_handler import logger


class AssertHandler:
    """
    断言封装 - 提供更清晰的断言方法和日志
    """

    @staticmethod
    def assert_code(response_json, expected_code=200):
        """断言业务状态码"""
        actual_code = response_json.get("code")
        try:
            assert actual_code == expected_code, \
                f"业务状态码不匹配: 期望={expected_code}, 实际={actual_code}, msg={response_json.get('msg')}"
            logger.info(f"✅ 断言通过: code={actual_code}")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_http_status(response, expected_status=200):
        """断言HTTP状态码"""
        actual_status = response.status_code
        try:
            assert actual_status == expected_status, \
                f"HTTP状态码不匹配: 期望={expected_status}, 实际={actual_status}"
            logger.info(f"✅ 断言通过: HTTP状态码={actual_status}")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_msg_contains(response_json, expected_text):
        """断言msg包含某文本"""
        actual_msg = response_json.get("msg", "")
        try:
            assert expected_text in actual_msg, \
                f"msg不包含预期文本: 期望包含='{expected_text}', 实际msg='{actual_msg}'"
            logger.info(f"✅ 断言通过: msg包含'{expected_text}'")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_has_field(data, field_name):
        """断言数据中包含某字段"""
        try:
            assert field_name in data, \
                f"响应数据缺少字段: '{field_name}', 实际字段: {list(data.keys())}"
            logger.info(f"✅ 断言通过: 包含字段'{field_name}'")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_equal(actual, expected, field_name=""):
        """断言两个值相等"""
        try:
            assert actual == expected, \
                f"{'[' + field_name + '] ' if field_name else ''}值不匹配: 期望={expected}, 实际={actual}"
            logger.info(f"✅ 断言通过: {field_name}={actual}")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_greater_than(actual, expected, field_name=""):
        """断言大于"""
        try:
            assert actual > expected, \
                f"{'[' + field_name + '] ' if field_name else ''}{actual} 不大于 {expected}"
            logger.info(f"✅ 断言通过: {field_name}={actual} > {expected}")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_list_not_empty(data_list, list_name="列表"):
        """断言列表不为空"""
        try:
            assert isinstance(data_list, list), f"{list_name} 不是列表类型"
            assert len(data_list) > 0, f"{list_name} 为空"
            logger.info(f"✅ 断言通过: {list_name}长度={len(data_list)}")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_db_exists(db, sql, params=None, msg="数据库记录"):
        """断言数据库记录存在"""
        result = db.query_one(sql, params)
        try:
            assert result is not None, f"{msg} 不存在: SQL={sql}, 参数={params}"
            logger.info(f"✅ 断言通过: {msg} 存在")
            return result
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_db_not_exists(db, sql, params=None, msg="数据库记录"):
        """断言数据库记录不存在"""
        result = db.query_one(sql, params)
        try:
            assert result is None, f"{msg} 应不存在但找到了: {result}"
            logger.info(f"✅ 断言通过: {msg} 不存在")
        except AssertionError as e:
            logger.error(f"❌ 断言失败: {str(e)}")
            raise