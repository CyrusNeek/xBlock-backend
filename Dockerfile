# Django Dockerfile for Cloud Run
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies and set locale
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    locales \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# Set locale
ENV LANG en_US.utf8

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and set locale
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-traditional \
    postgresql-client \
    libpq-dev \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# Set locale
ENV LANG en_US.utf8

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Create directories
RUN mkdir -p /app/staticfiles /app/media

# Copy application files
COPY requirements.txt manage.py ./
COPY xblock xblock/
COPY web web/
COPY report report/
COPY roles roles/
COPY accounting accounting/
COPY google_services google_services/
COPY subscription subscription/
COPY vtk vtk/
COPY xmeeting xmeeting/
COPY customer customer/
COPY pos pos/
COPY employee employee/
COPY reservation reservation/
COPY templates templates/

# Copy and set up entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set permissions for all files
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    STATIC_ROOT=/app/staticfiles \
    MEDIA_ROOT=/app/media \
    GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
    PATH="/usr/local/bin:${PATH}" \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=xblock.settings.production

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/health/ || exit 1

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
