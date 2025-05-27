# Build the container
docker build -t xblock-test .

# Get secrets from Google Cloud
$env:DATABASE_NAME = gcloud secrets versions access latest --secret=DATABASE_NAME
$env:DATABASE_USER = gcloud secrets versions access latest --secret=DATABASE_USER
$env:DATABASE_PASSWORD = gcloud secrets versions access latest --secret=DATABASE_PASSWORD
$env:DATABASE_HOST = gcloud secrets versions access latest --secret=DATABASE_HOST
$env:DATABASE_PORT = gcloud secrets versions access latest --secret=DATABASE_PORT
$env:SECRET_KEY = gcloud secrets versions access latest --secret=django-secret-key

# Run with similar environment to Cloud Run
docker run -it --rm `
  -p 8080:8080 `
  -e PORT=8080 `
  -e DJANGO_SETTINGS_MODULE=xblock.settings.production `
  -e DATABASE_NAME=$env:DATABASE_NAME `
  -e DATABASE_USER=$env:DATABASE_USER `
  -e DATABASE_PASSWORD=$env:DATABASE_PASSWORD `
  -e DATABASE_HOST=$env:DATABASE_HOST `
  -e DATABASE_PORT=$env:DATABASE_PORT `
  -e SECRET_KEY=$env:SECRET_KEY `
  -e PYTHONUNBUFFERED=1 `
  xblock-test
