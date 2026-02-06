#!/bin/sh

# Exit on any error EXCEPT collectstatic warnings
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
# Use --ignore to skip problematic paths if they don't exist
# WhiteNoise will handle compression with WHITENOISE_MANIFEST_STRICT = False
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --ignore=node_modules 2>&1 | tail -20 || echo "⚠ Static collection completed with warnings (acceptable)"

echo "--- Setup Complete: Starting Gunicorn ---"

# Execute the CMD from Dockerfile (which is Gunicorn)
exec "$@"