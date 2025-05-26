# Multi-stage build for Django application
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy project
COPY . .

# Set permissions for scripts
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/fallback.sh

# Create necessary directories and set permissions
RUN mkdir -p /app/staticfiles /app/media
RUN chown -R app:app /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    STATIC_ROOT=/app/staticfiles \
    MEDIA_ROOT=/app/media

# Switch to non-root user
USER app

# Expose port
EXPOSE 8080

# Use CMD instead of ENTRYPOINT for better Cloud Run compatibility
# This allows the container to gracefully handle signals
CMD ["/bin/bash", "-c", "/app/entrypoint.sh || /app/fallback.sh"]
