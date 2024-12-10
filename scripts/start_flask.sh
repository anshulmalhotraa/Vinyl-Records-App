#!/bin/bash

# Stop any existing Gunicorn processes on port 5000
echo "Stopping existing Gunicorn processes on port 5000..."
pkill -f "gunicorn.*5000"

# Activate the virtual environment
echo "Activating virtual environment..."
source /home/ubuntu/app/venv/bin/activate

# Navigate to the application directory
cd /home/ubuntu/app/src

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
