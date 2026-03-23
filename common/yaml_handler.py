# ===== common/yaml_handler.py =====

import yaml
import os


def read_yaml(file_path):
    """
    读取 YAML 文件
    :param file_path: 文件路径（相对于项目根目录）
    :return: 字典或列表
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, file_path)

    with open(full_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def read_config():
    """读取全局配置"""
    return read_yaml("config/config.yaml")


# 测试一下
if __name__ == "__main__":
    config = read_config()
    print(config)
    print(f"base_url: {config['base_url']}")