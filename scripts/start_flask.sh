#!/bin/bash

source /home/ec2-user/app/venv/bin/activate
cd /home/ec2-user/app
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
