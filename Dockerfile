# Multi-stage build for Django application
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy project
COPY . .
COPY entrypoint.sh /app/entrypoint.sh

# Set permissions
RUN chown -R app:app /app
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Expose port
EXPOSE 8080

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
