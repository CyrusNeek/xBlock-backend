<<<<<<< HEAD
=======
# Use the official slim Python base image
>>>>>>> master
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

<<<<<<< HEAD
# (Optional) Add a simple HTTP server as a placeholder
RUN echo "from http.server import SimpleHTTPRequestHandler, test; test(SimpleHTTPRequestHandler, port=8080)" > server.py

# Copy your backend files (if any)
# COPY . .

# Expose port expected by Cloud Run
EXPOSE 8080

# Start the Python HTTP server
CMD ["python", "server.py"]
=======
# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project
COPY . .

# Expose Cloud Run's required port
EXPOSE 8080

# Start Django using Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]
>>>>>>> master
