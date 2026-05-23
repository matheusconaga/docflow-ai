pipeline {

    agent any

    environment {
        DATABASE_URL = 'sqlite:///./test.db'
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
                sh 'docker build -t docflow-ai .'
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                docker run --rm \
                  -e DATABASE_URL=sqlite:///./test.db \
                  docflow-ai \
                  pytest --cov=app
                '''
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