#!/bin/bash

cd backend
echo "Python3 installing packages..."
pip3 install -r requirements.txt
python3 create_db.py
nohup python3 app.py &
sleep 3
curl http://localhost:5000/api/health
cd ../frontend
echo "NPM installing packages..."
npm install
nohup npm start &
