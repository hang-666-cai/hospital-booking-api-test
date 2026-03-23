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
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                sh """
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
                """
            }
        }

        stage('执行测试') {
            steps {
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