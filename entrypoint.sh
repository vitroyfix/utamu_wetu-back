#!/bin/sh

# Fail immediately if any command fails
set -e

echo "--- Render Simulation: Starting Setup ---"

# 1. Wait for DB (Render's internal DBs can take a second to accept connections)
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database connection..."
    sleep 3
fi

# 2. Apply Migrations (If this fails, Render will reject the deploy)
echo "Applying database migrations..."
python manage.py migrate --noinput

# 3. Collect Static Files (Crucial for production UI)
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "--- Setup Complete: Starting Gunicorn ---"

# Execute the CMD from Dockerfile (which is Gunicorn)
exec "$@"