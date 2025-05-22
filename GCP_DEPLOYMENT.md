# Google Cloud Platform Deployment Guide

This guide provides instructions for deploying the xBlock application to Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites

1. Google Cloud Platform account with billing enabled
2. Google Cloud SDK installed and configured
3. Docker installed locally (for testing)
4. Access to the xBlock GitHub repository

## Setting Up Secrets in Google Cloud Secret Manager

Before deploying the application, you need to set up the following secrets in Google Cloud Secret Manager:

1. **xblock-secret-key**: Django's SECRET_KEY
2. **xblock-db-password**: Database password
3. **xblock-gcp-credentials**: GCP service account credentials JSON
4. **xblock-integrations-credentials**: Integrations service account credentials JSON

### Steps to Create Secrets

```bash
# Create the secrets
gcloud secrets create xblock-secret-key --replication-policy="automatic"
gcloud secrets create xblock-db-password --replication-policy="automatic"
gcloud secrets create xblock-gcp-credentials --replication-policy="automatic"
gcloud secrets create xblock-integrations-credentials --replication-policy="automatic"

# Add versions to the secrets
echo -n "your-django-secret-key" | gcloud secrets versions add xblock-secret-key --data-file=-
echo -n "your-database-password" | gcloud secrets versions add xblock-db-password --data-file=-
# For JSON credentials, use a file
gcloud secrets versions add xblock-gcp-credentials --data-file=/path/to/your/gcp-credentials.json
gcloud secrets versions add xblock-integrations-credentials --data-file=/path/to/your/integrations-credentials.json
```

### Grant Access to Cloud Run Service Account

You need to grant the Cloud Run service account access to the secrets:

```bash
# Get your Cloud Run service account
SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Cloud Run Service Agent" --format="value(email)")

# Grant access to each secret
gcloud secrets add-iam-policy-binding xblock-secret-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding xblock-db-password \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding xblock-gcp-credentials \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding xblock-integrations-credentials \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

## Deploying to Cloud Run

The application is configured to be deployed to Cloud Run using Cloud Build. The `cloudbuild.prod.yaml` file defines the build and deployment process.

### Manual Deployment

If you want to deploy manually, you can use the following commands:

```bash
# Build the Docker image
docker build -t gcr.io/[PROJECT_ID]/xblock:latest .

# Push the image to Container Registry
docker push gcr.io/[PROJECT_ID]/xblock:latest

# Deploy to Cloud Run
gcloud run deploy xblock \
  --image gcr.io/[PROJECT_ID]/xblock:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --timeout 300s \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --update-secrets SECRET_KEY=xblock-secret-key:latest,DATABASE_PASSWORD=xblock-db-password:latest,GCP_CREDENTIALS=xblock-gcp-credentials:latest,INTEGRATIONS_CREDENTIALS=xblock-integrations-credentials:latest \
  --set-env-vars DEBUG=False,DATABASE_NAME=xblock,DATABASE_USER=xblock,DATABASE_HOST=db,DATABASE_PORT=5432,GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/gcp-credentials.json
```

### Automated Deployment with Cloud Build

To deploy using Cloud Build, push your changes to the GitHub repository. Cloud Build will automatically trigger a build and deployment process based on the `cloudbuild.prod.yaml` configuration.

```bash
# Push your changes to GitHub
git add .
git commit -m "Update configuration for GCP deployment"
git push origin main
```

## Verifying the Deployment

After deployment, you can verify that the application is running correctly:

```bash
# Get the URL of the deployed service
gcloud run services describe xblock --region us-central1 --format="value(status.url)"
```

Visit the URL to check if the application is responding correctly. You should see the Django application running.

## Troubleshooting

### Checking Logs

If you encounter issues, you can check the Cloud Run logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=xblock" --limit 50
```

### Common Issues

1. **Missing Secrets**: Ensure all required secrets are created in Secret Manager.
2. **Permission Issues**: Verify that the Cloud Run service account has access to the secrets.
3. **Database Connection**: Check that the database connection parameters are correct.
4. **Credential Files**: Ensure the entrypoint script is correctly writing the credential files.

## Local Development

For local development, copy `.env.sample` to `.env` and fill in the required values:

```bash
cp .env.sample .env
# Edit .env with your local configuration
```

Run the application locally with Docker:

```bash
docker-compose up
```

## Security Considerations

- Never commit sensitive credentials to the repository.
- Use Secret Manager for all sensitive information.
- Keep the `.env` file in your `.gitignore` to prevent accidental commits.
- Regularly rotate secrets and credentials.
