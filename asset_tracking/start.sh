#!/bin/bash

cd backend
pip3 install -r requirements.txt
python3 create_db.py
nohup python3 app.py &
sleep 3
curl http://localhost:5000/api/health
