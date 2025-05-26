# Simple Dockerfile for Django on Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    STATIC_ROOT=/app/staticfiles \
    MEDIA_ROOT=/app/media

# Expose port
EXPOSE 8080

# Simple direct command to start Gunicorn
CMD exec gunicorn xblock.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --log-level debug
