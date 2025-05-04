pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Verify Files') {
            steps {
                script {
                    if (!fileExists('main.html') || !fileExists('main.css')) {
                        error("Required files 'main.html' or 'main.css' are missing!")
                    } else {
                        echo "Files 'main.html' and 'main.css' found in the repository."
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                bat '''
                echo Deploying files...
                if not exist "C:\\deploy" mkdir C:\\deploy
                copy index.html C:\\deploy\\
                copy style.css C:\\deploy\\
                echo Deployment complete.
                '''
            }
        }
    }
}
}
