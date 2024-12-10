ubuntu@ip-172-31-22-80:~/app/src/scripts$ cat start_flask.sh
#!/bin/bash

# Activate the virtual environment
source /home/ubuntu/app/venv/bin/activate

# Navigate to the app's source directory
cd /home/ubuntu/app/src

# Stop any running Gunicorn process
pkill -f "gunicorn --workers 3 --bind 0.0.0.0:5000" || true

# Start Gunicorn in the background
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app &
