# Use the official slim Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the Django project
COPY . .

# Expose Cloud Run's required port
EXPOSE 8080

# Start Django using Gunicorn on port 8080
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]
