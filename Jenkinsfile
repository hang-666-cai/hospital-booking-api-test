pipeline {
    agent any

    parameters {
        choice(name: 'TEST_SCOPE', choices: ['all', 'smoke'], description: '选择测试范围')
    }

    environment {
        // Linux 路径使用正斜杠
        ALLURE_RESULTS = 'reports/allure-results'
    }

    stages {
        stage('拉取代码') {
            steps {
                echo "开始拉取 GitHub 代码..."
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                echo "正在安装 Python 依赖..."
                // 1. 使用 sh 代替 bat
                // 2. Linux 中通常使用 python3
                // 3. 激活虚拟环境使用 source 或 .
                sh """
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
                """
            }
        }

        stage('执行测试') {
            steps {
                echo "正在执行测试范围: ${params.TEST_SCOPE}"
                // Linux 的 if 语法与 Windows 不同
                sh """
                . venv/bin/activate
                if [ "${params.TEST_SCOPE}" = "all" ]; then
                    pytest testcases/ -v --alluredir=${ALLURE_RESULTS} --clean-alluredir
                else
                    pytest testcases/ -v -m smoke --alluredir=${ALLURE_RESULTS} --clean-alluredir
                fi
                """
            }
        }

        stage('生成报告') {
            steps {
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