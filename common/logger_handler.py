# ===== common/logger_handler.py =====

import logging
import os
from datetime import datetime


def setup_logger(name="api_test"):
    """
    配置日志
    :param name: 日志名称
    :return: logger 对象
    """
    # 创建日志目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名（按天）
    log_file = os.path.join(
        log_dir,
        f"test_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    # 文件 handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 格式
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 创建全局 logger 实例（其他文件直接导入这个）
logger = setup_logger()


# 测试
if __name__ == "__main__":
    logger.debug("这是 debug 信息")
    logger.info("这是 info 信息")
    logger.warning("这是 warning 信息")
    logger.error("这是 error 信息")