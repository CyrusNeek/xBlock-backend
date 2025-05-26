import os
import sys
from pathlib import Path
from google.cloud import secretmanager

def access_secret_version(project_id, secret_id, version_id="latest"):
    """Access the secret version."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def main():
    # Get the project ID from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Load secrets from Secret Manager
    try:
        # Load backend environment variables
        backend_env = access_secret_version(project_id, "backend-env")
        with open("/app/.env", "w") as f:
            f.write(backend_env)

        # Load Django settings module
        django_settings = access_secret_version(project_id, "xblock-django-settings-module")
        os.environ["DJANGO_SETTINGS_MODULE"] = django_settings

    except Exception as e:
        print(f"Error loading secrets: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Run Django migrations
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(["manage.py", "migrate"])
    except Exception as e:
        print(f"Error running migrations: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Start Gunicorn
    try:
        import gunicorn.app.wsgi
        gunicorn.app.wsgi.run(
            "xblock.wsgi:application",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            workers=2,
            timeout=300,
            accesslog="-",
            errorlog="-",
            loglevel="info"
        )
    except Exception as e:
        print(f"Error starting Gunicorn: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 