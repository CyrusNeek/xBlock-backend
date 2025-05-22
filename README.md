# xBlock - Minimal Django Project

A minimal Django 4.1.4 project for testing Cloud Run deployment.

## Project Structure

- `xblock/` - Django project settings, urls, wsgi
- `web/` - Simple Django app with placeholder model
- `manage.py` - Django management script

## Deployment Files

- `Dockerfile` - Multi-stage build with Python 3.11-slim
- `cloudbuild.prod.yaml` - GCP Cloud Run deployment configuration
- `entrypoint.sh` - Container startup script
- `requirements.txt` - Django dependencies
- `.dockerignore` - Files to exclude from Docker build
- `.env` - Environment variables (for local development)

## Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

## Cloud Run Deployment

This project is configured for deployment to Google Cloud Run using Cloud Build.

The deployment process is optimized for speed (under 3-4 minutes) and includes:
- Health check endpoints at `/healthz` and `/`
- Proper PORT configuration (default: 8080)
- Secure environment variable handling

## Docker

To build and run locally with Docker:

```
docker build -t xblock .
docker run -p 8080:8080 xblock
```
