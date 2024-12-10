#!/bin/bash

source /home/ubuntu/app/venv/bin/activate
cd /home/ubuntu/app
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
