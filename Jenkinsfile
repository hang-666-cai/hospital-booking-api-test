pipeline {
    agent {
        docker {
            image 'python:3.9'           // 使用官方 Python 镜像作为构建环境
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    parameters {
        choice(name: 'TEST_SCOPE', choices: ['all', 'smoke'], description: '选择测试范围')
    }

    environment {
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
                sh """
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
                """
            }
        }

        stage('执行测试') {
            steps {
                echo "正在执行测试范围: ${params.TEST_SCOPE}"
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