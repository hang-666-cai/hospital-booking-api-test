# ===== common/base_api.py =====

import requests
import json
from common.logger_handler import logger
from common.yaml_handler import read_config


class BaseApi:
    """
    请求基类 - 所有接口类的父类
    封装统一的请求发送、日志记录、响应处理
    """

    def __init__(self):
        self.session = requests.Session()
        self.config = read_config()
        self.base_url = self.config["base_url"]
        self.token = None

    def set_token(self, token):
        """设置 Token 到请求头"""
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        logger.info(f"Token 已设置: {token[:20]}...")

    def clear_token(self):
        """清除 Token"""
        self.token = None
        self.session.headers.pop("Authorization", None)
        logger.info("Token 已清除")

    def send_request(self, method, url, **kwargs):
        """
        统一请求方法
        :param method: 请求方法 GET/POST/PUT/DELETE
        :param url: 接口路径（不包含 base_url）
        :param kwargs: 其他参数（params, json, data, headers 等）
        :return: Response 对象
        """
        # 拼接完整 URL
        full_url = self.base_url + url

        # 打印请求信息
        logger.info("=" * 60)
        logger.info(f"请求方法: {method}")
        logger.info(f"请求地址: {full_url}")

        if "params" in kwargs:
            logger.info(f"查询参数: {kwargs['params']}")
        if "json" in kwargs:
            logger.info(f"请求Body: {json.dumps(kwargs['json'], ensure_ascii=False)}")
        if "data" in kwargs:
            logger.info(f"表单数据: {kwargs['data']}")

        # 发送请求
        try:
            response = self.session.request(method, full_url, **kwargs)

            # 打印响应信息
            logger.info(f"响应状态码: {response.status_code}")
            # 限制日志长度，避免超长响应刷屏
            response_text = response.text
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "...(截断)"
            logger.info(f"响应数据: {response_text}")
            logger.info("=" * 60)

            return response

        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            raise

    def get(self, url, params=None, **kwargs):
        """GET 请求"""
        return self.send_request("GET", url, params=params, **kwargs)

    def post(self, url, json=None, data=None, **kwargs):
        """POST 请求"""
        return self.send_request("POST", url, json=json, data=data, **kwargs)

    def put(self, url, json=None, **kwargs):
        """PUT 请求"""
        return self.send_request("PUT", url, json=json, **kwargs)

    def delete(self, url, **kwargs):
        """DELETE 请求"""
        return self.send_request("DELETE", url, **kwargs)