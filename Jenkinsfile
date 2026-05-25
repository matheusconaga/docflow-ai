pipeline {

    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }

    environment {

        DATABASE_URL = credentials('neon-database-url')
        DATABASE_TEST_URL = credentials('neon-test-database-url')

        IMAGE_NAME = "docflow-ai:${BUILD_NUMBER}"
        IMAGE_LATEST = "docflow-ai:latest"

        CONTAINER_NAME = "docflow-api"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build \
                  -t $IMAGE_NAME \
                  -t $IMAGE_LATEST \
                  .
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                docker run --rm \
                  -e DATABASE_URL="$DATABASE_TEST_URL" \
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
                  -e DATABASE_URL="$DATABASE_URL" \
                  -v $(pwd)/app/storage/uploads:/app/app/storage/uploads \
                  $IMAGE_LATEST
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