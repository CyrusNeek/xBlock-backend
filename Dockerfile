# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Speed up builds by reducing logs and skipping cache
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Optional: Install system dependencies if needed by any Python packages
# RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean
# For this minimal Django app, build-essential and libpq-dev might not be strictly necessary
# unless a specific package in requirements.txt needs them. Let's remove them for a truly minimal setup.
RUN apt-get update && apt-get install -y --no-install-recommends gcc && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
# Install dependencies to a specific location that will be copied to the runner stage
RUN pip install --target=/install -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=xblock.settings

# Copy installed packages from builder stage's /install directory
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copy the project code
# We need manage.py, the xblock project directory, and the web app directory, and entrypoint.sh
COPY manage.py ./manage.py
COPY xblock/ ./xblock/
COPY web/ ./web/
COPY entrypoint.sh ./entrypoint.sh

# Ensure entrypoint.sh is executable
RUN chmod +x ./entrypoint.sh

# Expose the port Gunicorn will run on
EXPOSE ${PORT:-8080}

# Run the entrypoint script
CMD ["./entrypoint.sh"]
