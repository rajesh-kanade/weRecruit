echo "Starting web app"
nohup python3 ./src/werecruit/webApp.py &

echo "Starting scheduler"
nohup python3 ./src/werecruit/cronjobs.py &

echo "weRecruit started !!!"

