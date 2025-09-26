#!/bin/bash
# Navigate to backend directory
cd "/mnt/d/Web App Data Audit/Frontend/backend" || exit 1

# Activate venv
source wslvenv/bin/activate

# Start Redis (if not already running in WSL)
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
else
    echo "Redis already running."
fi

# Start worker in foreground (logs visible)
echo "Starting RQ worker..."
rq worker --url redis://localhost:6379 default &
WORKER_PID=$!

# Start Flask app
echo "Starting Flask app..."
python Application.py

# Cleanup worker when Flask exits
kill $WORKER_PID
