pipeline {
    agent any

    environment {
        MONGO_URI  = credentials('MONGO_URI')
        STAGING_IP = credentials('STAGING_IP')
        PROD_IP    = credentials('PROD_IP')
    }

    stages {

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
                    bandit -r . --exclude ./venv,./tests -s B101,B104
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

        stage('Deploy Staging') {
            when {
                branch 'staging'
            }
            steps {
                sshagent(['staging-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@$STAGING_IP bash -s << 'ENDSSH'
set -e
APP_DIR=/var/www/flask-app
echo "Deploying Staging"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p "$APP_DIR"
    sudo chown -R ubuntu:ubuntu "$APP_DIR"
    git clone -b staging https://github.com/Avinashsain/flask-ci-cd-app.git "$APP_DIR"
    cd "$APP_DIR"
else
    cd "$APP_DIR"
    if [ -f ".env" ]; then
        cp .env /tmp/flask_app_env_backup
        echo "Backed up .env"
    fi
    git fetch origin
    git reset --hard origin/staging
    if [ -f "/tmp/flask_app_env_backup" ]; then
        cp /tmp/flask_app_env_backup .env
        echo "Restored .env"
    fi
fi
cd "$APP_DIR"
if [ ! -f ".env" ]; then
    echo "ERROR: .env missing!"
    exit 1
fi
echo "Current .env:"
cat .env
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl restart flask-app
sudo systemctl restart nginx
echo "Staging Done"
ENDSSH
                    '''
                }
            }
        }

        stage('Deploy Production') {
            when {
                branch 'master'
            }
            steps {
                sshagent(['prod-ssh']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@$PROD_IP bash -s << 'ENDSSH'
set -e
APP_DIR=/var/www/flask-app
echo "Deploying Production"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p "$APP_DIR"
    sudo chown -R ubuntu:ubuntu "$APP_DIR"
    git clone -b master https://github.com/Avinashsain/flask-ci-cd-app.git "$APP_DIR"
    cd "$APP_DIR"
else
    cd "$APP_DIR"
    if [ -f ".env" ]; then
        cp .env /tmp/flask_app_env_backup
        echo "Backed up .env"
    fi
    git fetch origin
    git reset --hard origin/master
    if [ -f "/tmp/flask_app_env_backup" ]; then
        cp /tmp/flask_app_env_backup .env
        echo "Restored .env"
    fi
fi
cd "$APP_DIR"
if [ ! -f ".env" ]; then
    echo "ERROR: .env missing!"
    exit 1
fi
echo "Current .env:"
cat .env
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl restart flask-app
sudo systemctl restart nginx
echo "Production Done"
ENDSSH
                    '''
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline passed on branch: ${env.BRANCH_NAME}"
        }
        failure {
            echo "Pipeline FAILED on branch: ${env.BRANCH_NAME}"
        }
    }
}