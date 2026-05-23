pipeline {

    agent any

    environment {
        DATABASE_URL = 'sqlite:///./test.db'
        IMAGE_NAME = "docflow-ai:${BUILD_NUMBER}"
        CONTAINER_NAME = "docflow-api"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/matheusconaga/docflow-ai.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                docker run --rm \
                  -e DATABASE_URL=$DATABASE_URL \
                  $IMAGE_NAME \
                  pytest --cov=app -v
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
            echo 'Pipeline executada com sucesso 🚀'
        }

        failure {
            echo 'Pipeline falhou ❌'
        }
    }
}