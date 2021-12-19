#!/bin/bash

echo "Starting weRecruit web app"
gunicorn --pythonpath /etc/werecruit/src/werecruit --daemon --workers 4 --bind 0.0.0.0:5000 webApp:app

echo "Starting weRecruit scheduler"
nohup python3 ./src/werecruit/cronjobs.py & #wr_sched

echo 
echo "weRecruit all processes started."



