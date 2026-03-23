# ===== common/db_handler.py =====

import pymysql
from common.yaml_handler import read_config
from common.logger_handler import logger


class DBHandler:
    """数据库操作封装"""

    def __init__(self):
        config = read_config()["database"]
        self.config = config
        self.conn = self._connect()
        logger.info(f"数据库连接成功: {config['host']}:{config['port']}/{config['database']}")

    def _connect(self):
        """创建数据库连接"""
        return pymysql.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True  # ★ 关键：自动提交，每次查询都能读到最新数据
        )

    def _ensure_connection(self):
        """确保连接可用，断线重连"""
        try:
            self.conn.ping(reconnect=True)
        except Exception:
            self.conn = self._connect()

    def query_one(self, sql, params=None):
        """查询单条记录"""
        self._ensure_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            logger.debug(f"SQL查询: {sql} | 参数: {params} | 结果: {result}")
            return result

    def query_all(self, sql, params=None):
        """查询多条记录"""
        self._ensure_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            logger.debug(f"SQL查询: {sql} | 参数: {params} | 结果数量: {len(result)}")
            return result

    def query_count(self, sql, params=None):
        """查询数量"""
        self._ensure_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return list(result.values())[0] if result else 0

    def execute(self, sql, params=None):
        """执行增删改"""
        self._ensure_connection()
        with self.conn.cursor() as cursor:
            affected = cursor.execute(sql, params)
            self.conn.commit()
            logger.debug(f"SQL执行: {sql} | 参数: {params} | 影响行数: {affected}")
            return affected

    def close(self):
        """关闭连接"""
        try:
            if self.conn and self.conn.open:
                self.conn.close()
                logger.info("数据库连接已关闭")
        except Exception:
            pass