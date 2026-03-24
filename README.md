# 智慧医疗预约挂号平台 - 接口自动化测试

## 项目简介

基于 Python + Requests + Pytest + Allure 搭建的接口自动化测试框架，
针对智慧医疗预约挂号平台进行全面的接口测试。

## 技术栈

- Python 3.8+
- Requests（HTTP请求）
- Pytest（测试框架）
- Allure（测试报告）
- PyMySQL（数据库验证）
- YAML（数据驱动）
- Jenkins（持续集成）

## 项目结构

api_test/
├── api/ # 接口封装层
├── common/ # 公共工具层
├── config/ # 配置文件
├── data/ # 测试数据（YAML）
├── testcases/ # 测试用例
├── reports/ # 测试报告
├── logs/ # 日志
├── conftest.py # Pytest全局配置
├── pytest.ini # Pytest配置
└── requirements.txt # 依赖包

## 框架特点

- 四层架构：数据层 + 公共层 + 接口层 + 用例层
- 数据驱动：YAML文件管理测试数据，数据与代码分离
- 统一封装：请求基类封装、断言封装、日志封装
- 数据库验证：接口响应 + 数据库双重断言
- 可视化报告：Allure生成详细测试报告
- CI/CD集成：Jenkins定时执行 + 通知

## 测试覆盖

| 模块     | 用例数  | 覆盖接口数 |
| -------- | ------- | ---------- |
| 用户认证 | 15      | 5          |
| 医院查询 | 7       | 2          |
| 科室查询 | 3       | 2          |
| 医生查询 | 3       | 2          |
| 排班查询 | 3       | 2          |
| 预约挂号 | 10      | 4          |
| 管理端   | 8       | 15+        |
| 权限安全 | 5       | 5+         |
| **合计** | **54+** | **37+**    |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 修改配置

编辑 `config/config.yaml`，修改数据库连接和服务地址。

### 3. 运行测试

Bash



```
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 测试报告截图

![image-20260324131705752](C:\Users\蔡志航\AppData\Roaming\Typora\typora-user-images\image-20260324131705752.png)

![image-20260324131817703](C:\Users\蔡志航\AppData\Roaming\Typora\typora-user-images\image-20260324131817703.png)# 智慧医疗预约挂号平台 - 接口自动化测试

