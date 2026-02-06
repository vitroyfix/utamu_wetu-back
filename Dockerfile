FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 10000

WORKDIR /app

# Install system dependencies
# We keep these in one layer to reduce image size
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# --- OPTIMIZATION FOR RENDER ---
# Pre-collect static files during build. 
# This prevents Render from timing out during the 'start' phase.
# '|| true' ensures the build doesn't fail if variables aren't present yet.
RUN python manage.py collectstatic --noinput || true

# Setup entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Use the shell form to ensure the $PORT variable from Render is used
CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT