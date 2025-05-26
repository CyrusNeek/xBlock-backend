# Ultra-minimal Dockerfile for Cloud Run debug server
FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir gunicorn flask

# Copy only essential files
COPY minimal_server.py /app/

# Set environment variables
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run a simple Flask server that will definitely start
CMD exec gunicorn --bind 0.0.0.0:$PORT minimal_server:app
