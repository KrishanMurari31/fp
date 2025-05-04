pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/KrishanMurari31/fp.git', branch: 'master'
            }
        }

        stage('Verify Files') {
            steps {
                echo 'Verifying files by opening the main webpage...'
                script {
                    def htmlFile = 'main.html'
                    if (fileExists(htmlFile)) {
                        echo "Opening ${htmlFile}..."
                        if (isUnix()) {
                            sh "xdg-open ${htmlFile} || echo 'xdg-open not available'"
                        } else {
                            bat "start ${htmlFile}"
                        }
                    } else {
                        error "Main web page (${htmlFile}) not found!"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Add your deployment logic here
            }
        }
    }
}
