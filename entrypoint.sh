#!/bin/sh

# Run Alembic migrations
echo "Running migrations"
alembic upgrade head

# Start FastAPI application
echo "Starting FastAPI application"
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
