#!/bin/bash
# Start script for Cloud Run - runs both Celery worker and Uvicorn API

set -e  # Exit on error

echo "Starting SmartSupport Backend..."

# Get port from environment variable (Cloud Run sets this to 8080)
PORT=${PORT:-8000}

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 2

# Check if Celery started successfully
if ! kill -0 $CELERY_PID 2>/dev/null; then
    echo "ERROR: Celery worker failed to start"
    exit 1
fi

echo "Celery worker started (PID: $CELERY_PID)"

# Start Uvicorn API in foreground (this keeps the container alive)
echo "Starting Uvicorn API on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Note: If Uvicorn exits, the container will stop
# Cloud Run will restart the container automatically

