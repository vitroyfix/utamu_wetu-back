FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 10000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
# Using --no-cache-dir to force a fresh download from PyPI
RUN pip install --no-cache-dir -r requirements.txt

# DEBUG: This will print installed packages to your Render logs
RUN pip list

# Copy project files
COPY . /app/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT