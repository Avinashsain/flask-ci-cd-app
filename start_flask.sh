#!/bin/bash

set -e  # stop on error

cd /var/www/flask-app

echo "Pulling latest code..."
git pull origin staging

echo "Activating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Restarting Flask service..."
sudo systemctl restart flask-app

echo "Deployment successful!"