# syntax=docker/dockerfile:1
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Cloud Run expects the service to listen on $PORT
ENV PORT=8080

# Use gunicorn as entrypoint
CMD exec gunicorn xblock.wsgi:application --bind 0.0.0.0:$PORT --workers 3
