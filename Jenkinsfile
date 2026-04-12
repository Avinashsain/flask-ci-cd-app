pipeline {
    agent any

    environment {
        MONGO_URI = credentials('mongo-uri')   // store in Jenkins credentials
    }

    stages {

        // ---------------- CI ----------------
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Avinashsain/flask-ci-cd-app.git',
                    branch: env.BRANCH_NAME ?: 'master'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt pytest pylint bandit
                '''
            }
        }

        stage('Lint & Security') {
            steps {
                sh '''
                    . venv/bin/activate
                    pylint app.py || true
                    bandit -r . -x venv,tests -s B101,B104
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v
                '''
            }
        }

        // ---------------- STAGING ----------------
        stage('Deploy Staging') {
            when {
                branch 'staging'
            }
            steps {
                sshagent(['staging-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${env.STAGING_IP} \
                            APP_DIR=/var/www/flask-app \
                            MONGO_URI='${env.MONGO_URI}' \
                            bash -s << 'EOF'
                        set -e
                        echo "Deploying Staging"

                        sudo rm -rf "\$APP_DIR"
                        sudo mkdir -p "\$APP_DIR"
                        sudo chown -R ubuntu:ubuntu "\$APP_DIR"
                        cd "\$APP_DIR"

                        git clone -b staging https://github.com/Avinashsain/flask-ci-cd-app.git .

                        echo "MONGO_URI=\${MONGO_URI}" > .env

                        python3 -m venv venv
                        . venv/bin/activate

                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install gunicorn

                        sudo systemctl daemon-reload
                        sudo systemctl enable flask-app
                        sudo systemctl restart flask-app
                        sudo systemctl restart nginx

                        echo "Staging Done"
                    EOF
                    """
                }
            }
        }

        // ---------------- PRODUCTION ----------------
        stage('Deploy Production') {
            when {
                branch 'master'
            }
            steps {
                sshagent(['prod-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${env.PROD_IP} \
                            APP_DIR=/var/www/flask-app \
                            MONGO_URI='${env.MONGO_URI}' \
                            bash -s << 'EOF'
                        set -e
                        echo "Deploying Production"

                        sudo rm -rf "\$APP_DIR"
                        sudo mkdir -p "\$APP_DIR"
                        sudo chown -R ubuntu:ubuntu "\$APP_DIR"
                        cd "\$APP_DIR"

                        git clone -b master https://github.com/Avinashsain/flask-ci-cd-app.git .

                        echo "MONGO_URI=\${MONGO_URI}" > .env

                        python3 -m venv venv
                        . venv/bin/activate

                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install gunicorn

                        sudo systemctl daemon-reload
                        sudo systemctl enable flask-app
                        sudo systemctl restart flask-app
                        sudo systemctl restart nginx

                        echo "Production Done"
                    EOF
                    """
                }
            }
        }
    }

    // ---------------- NOTIFICATIONS ----------------
    post {
        success {
            echo "Pipeline passed on branch: ${env.BRANCH_NAME}"
        }
        failure {
            echo "Pipeline FAILED on branch: ${env.BRANCH_NAME}"
        }
    }
}