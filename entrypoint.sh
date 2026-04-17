#!/bin/sh

echo "Waiting for database..."
sleep 15

echo "Running migrations..."
python -m alembic upgrade head

echo "Starting FastAPI..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000