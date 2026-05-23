pipeline {

    agent any

    environment {
        IMAGE_NAME = "docflow-ai"
        CONTAINER_NAME = "docflow-api"
    }

    stages {

        stage('Checkout') {

            steps {
                git 'https://github.com/matheusconaga/docflow-ai.git'
            }
        }

        stage('Install Dependencies') {

            steps {

                sh '''
                python -m venv venv

                . venv/bin/activate

                pip install --upgrade pip

                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {

            steps {

                sh '''
                . venv/bin/activate

                pytest \
                --cov=app \
                --cov-report=term \
                --cov-report=html \
                --cov-fail-under=90 \
                tests/
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Deploy Container') {

            steps {

                sh '''
                docker stop $CONTAINER_NAME || true

                docker rm $CONTAINER_NAME || true

                docker run -d \
                    --name $CONTAINER_NAME \
                    -p 8000:8000 \
                    $IMAGE_NAME
                '''
            }
        }
    }

    post {

        success {

            echo 'Pipeline executado com sucesso!'
        }

        failure {

            echo 'Pipeline falhou.'
        }
    }
}