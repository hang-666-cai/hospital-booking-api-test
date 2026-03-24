pipeline {
    agent any

    parameters {
        choice(name: 'TEST_SCOPE', choices: ['all', 'smoke'], description: '选择测试范围')
    }

    environment {
        ALLURE_RESULTS = 'reports/allure-results'
    }

    stages {
        stage('拉取代码') {
            steps {
                echo "开始拉取代码..."
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                echo "安装 Python 依赖..."
                bat """
                python -m venv venv
                call venv\\Scripts\\activate
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
                """
            }
        }

        stage('执行测试') {
            steps {
                echo "执行测试: ${params.TEST_SCOPE}"
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