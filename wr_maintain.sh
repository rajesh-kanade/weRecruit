#!/bin/bash

echo "Starting maintenance"
cd /etc/werecruit

echo "Deleting *.log files"
rm *.log

echo "Deleting *.out files"
rm *.out

echo "Completed maintenance."

