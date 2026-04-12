pipeline {
    agent any

    stages {

        // ---------------- CI ----------------
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Avinashsain/flask-ci-cd-app.git'
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
                    ssh -o StrictHostKeyChecking=no ubuntu@${env.STAGING_IP} << EOF
                    set -e

                    echo "🚀 Staging Deploy"

                    APP_DIR="/var/www/flask-app"
                    sudo rm -rf \$APP_DIR
                    sudo mkdir -p \$APP_DIR
                    sudo chown -R ubuntu:ubuntu \$APP_DIR
                    cd \$APP_DIR

                    git clone -b staging https://github.com/Avinashsain/flask-ci-cd-app.git .

                    echo "MONGO_URI=${env.MONGO_URI}" > .env

                    python3 -m venv venv
                    source venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install gunicorn

                    sudo systemctl daemon-reload
                    sudo systemctl enable flask-app
                    sudo systemctl restart flask-app
                    sudo systemctl restart nginx

                    echo "✅ Staging Done"
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
                    ssh -o StrictHostKeyChecking=no ubuntu@${env.PROD_IP} << EOF
                    set -e

                    echo "🚀 Production Deploy"

                    APP_DIR="/var/www/flask-app"
                    sudo rm -rf \$APP_DIR
                    sudo mkdir -p \$APP_DIR
                    sudo chown -R ubuntu:ubuntu \$APP_DIR
                    cd \$APP_DIR

                    git clone -b master https://github.com/Avinashsain/flask-ci-cd-app.git .

                    echo "MONGO_URI=${env.MONGO_URI}" > .env

                    python3 -m venv venv
                    source venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install gunicorn

                    sudo systemctl daemon-reload
                    sudo systemctl enable flask-app
                    sudo systemctl restart flask-app
                    sudo systemctl restart nginx

                    echo "✅ Production Done"
                    EOF
                    """
                }
            }
        }
    }
}