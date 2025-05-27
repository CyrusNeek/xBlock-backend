#!/bin/bash

# Build the container
docker build -t xblock-test .

# Run with similar environment to Cloud Run
docker run -it --rm \
  -p 8080:8080 \
  -e PORT=8080 \
  -e DJANGO_SETTINGS_MODULE=xblock.settings.production \
  -e DATABASE_NAME="$(gcloud secrets versions access latest --secret=DATABASE_NAME)" \
  -e DATABASE_USER="$(gcloud secrets versions access latest --secret=DATABASE_USER)" \
  -e DATABASE_PASSWORD="$(gcloud secrets versions access latest --secret=DATABASE_PASSWORD)" \
  -e DATABASE_HOST="$(gcloud secrets versions access latest --secret=DATABASE_HOST)" \
  -e DATABASE_PORT="$(gcloud secrets versions access latest --secret=DATABASE_PORT)" \
  -e SECRET_KEY="$(gcloud secrets versions access latest --secret=django-secret-key)" \
  -e PYTHONUNBUFFERED=1 \
  xblock-test
