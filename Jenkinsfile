pipeline {
    agent any

    environment {
        MONGO_URI = "mongodb://localhost:27017/testdb"
        APP_DIR = "/var/www/flask-app"
    }

    stages {

        // ---------------- CI ----------------
        stage('Checkout') {
            steps {
                git branch: "staging", url: 'https://github.com/Avinashsain/flask-ci-cd-app.git'
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
                bandit -r . -s B104,B101
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
                    sh '''
                    ssh -o StrictHostKeyChecking=no ubuntu@STAGING_IP << EOF
                    set -e

                    APP_DIR="/var/www/flask-app"
                    echo "🚀 Staging Deploy"

                    sudo rm -rf $APP_DIR
                    sudo mkdir -p $APP_DIR
                    sudo chown -R ubuntu:ubuntu $APP_DIR
                    cd $APP_DIR

                    git clone -b staging https://github.com/Avinashsain/flask-ci-cd-app.git .

                    echo "MONGO_URI=${MONGO_URI}" > .env

                    sudo apt update -y
                    sudo apt install -y python3-venv python3-pip nginx

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
                    '''
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
                    sh '''
                    ssh -o StrictHostKeyChecking=no ubuntu@PROD_IP << EOF
                    set -e

                    APP_DIR="/var/www/flask-app"
                    echo "🚀 Production Deploy"

                    sudo rm -rf $APP_DIR
                    sudo mkdir -p $APP_DIR
                    sudo chown -R ubuntu:ubuntu $APP_DIR
                    cd $APP_DIR

                    git clone -b master https://github.com/Avinashsain/flask-ci-cd-app.git .

                    echo "MONGO_URI=${MONGO_URI}" > .env

                    sudo apt update -y
                    sudo apt install -y python3-venv python3-pip nginx

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
                    '''
                }
            }
        }
    }
}