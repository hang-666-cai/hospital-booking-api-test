pipeline {
    agent any

    parameters {
        choice(name: 'TEST_SCOPE', choices: ['all', 'smoke'], description: '选择测试范围')
    }

    environment {
        // 设置报告存放路径
        ALLURE_RESULTS = 'reports/allure-results'
    }

    stages {
        stage('拉取代码') {
            steps {
                // Jenkins 会根据配置自动从 GitHub 拉取，这里打印一下信息
                echo "开始拉取 GitHub 代码..."
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                echo "正在安装 Python 依赖..."
                // Windows 环境使用 bat，Linux 环境使用 sh
                bat """
                python -m venv venv
                call venv\\Scripts\\activate
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
                """
            }
        }

        stage('执行测试') {
            steps {
                echo "正在执行测试范围: ${params.TEST_SCOPE}"
                // 运行 pytest
                bat """
                call venv\\Scripts\\activate
                if "${params.TEST_SCOPE}" == "all" (
                    pytest testcases/ -v --alluredir=${ALLURE_RESULTS} --clean-alluredir
                ) else (
                    pytest testcases/ -v -m smoke --alluredir=${ALLURE_RESULTS} --clean-alluredir
                )
                """
            }
        }

        stage('生成报告') {
            steps {
                // 这里的 results 路径要和 pytest 命令中的 --alluredir 一致
                // jdk: '' 表示使用系统默认 Java
                allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_RESULTS}"]]
            }
        }
    }

    post {
        always {
            echo "流水线执行完毕"
        }
    }
}