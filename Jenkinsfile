pipeline {

    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }

    environment {

        // Jenkins Credentials -> Secret text
        // ID: neon-database-url
        DATABASE_URL = credentials('neon-database-url')

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

        stage('Init Database') {
            steps {
                sh '''
                docker run --rm \
                  -e DATABASE_URL="$DATABASE_URL" \
                  $IMAGE_NAME \
                  python -m app.db.create_tables
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                docker run --rm \
                  -e DATABASE_URL="$DATABASE_URL" \
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

        always {
            sh 'docker image prune -f || true'
        }
    }
}