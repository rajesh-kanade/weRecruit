#!/bin/bash

echo "trying to stop gunicorn process"
pkill gunicorn

echo "Find the process id related to cronjobs.py"
ps ax|grep cronjobs.py

