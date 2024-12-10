#!/bin/bash

# Activate the virtual environment
echo "Activating the virtual environment..."
source /home/ubuntu/app/venv/bin/activate

# Navigate to the application directory
echo "Navigating to the application directory..."
cd /home/ubuntu/app/src

# Check if Gunicorn is already running
if pgrep -f "gunicorn.*5000" > /dev/null; then
  echo "Gunicorn is already running. Restarting it..."
  pkill -f "gunicorn.*5000"  # Stop the current Gunicorn process
else
  echo "Gunicorn is not running. Starting it now..."
fi

# Start Gunicorn in the background
echo "Starting Gunicorn..."
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app &
