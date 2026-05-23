pipeline {

    agent any

    stages {

        stage('Checkout') {

            steps {

                git branch: 'main',
                url: 'https://github.com/matheusconaga/docflow-ai.git'
            }
        }

        stage('Install Dependencies') {

            steps {

                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {

            steps {

                sh '''
                . venv/bin/activate
                pytest --cov=app
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh 'docker build -t docflow-ai .'
            }
        }

        stage('Deploy Container') {

            steps {

                sh '''
                docker stop docflow-api || true
                docker rm docflow-api || true

                docker run -d \
                  --name docflow-api \
                  -p 8000:8000 \
                  docflow-ai
                '''
            }
        }
    }

    post {

        success {

            echo 'Pipeline executada com sucesso!'
        }

        failure {

            echo 'Pipeline falhou.'
        }
    }
}