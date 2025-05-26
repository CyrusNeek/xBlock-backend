import os
import sys
import time
from pathlib import Path

def main():
    print("Starting application...", file=sys.stderr)
    
    # Set default environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
    
    # Check if we're running in Cloud Run
    if os.getenv('K_SERVICE'):  # Cloud Run sets this environment variable
        print("Running in Cloud Run environment", file=sys.stderr)
        # In Cloud Run, secrets are already mounted as environment variables
        # No need to load from Secret Manager
    else:
        print("Running in local environment", file=sys.stderr)
        try:
            from google.cloud import secretmanager
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                print("Error: GOOGLE_CLOUD_PROJECT environment variable not set", file=sys.stderr)
                sys.exit(1)

            def access_secret_version(secret_id, version_id="latest"):
                """Access the secret version."""
                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")

            # Load backend environment variables
            backend_env = access_secret_version("backend-env")
            with open("/app/.env", "w") as f:
                f.write(backend_env)
        except Exception as e:
            print(f"Warning: Could not load secrets from Secret Manager: {str(e)}", file=sys.stderr)
            print("Continuing with existing environment variables...", file=sys.stderr)

    # Run Django migrations
    try:
        from django.core.management import execute_from_command_line
        print("Running database migrations...", file=sys.stderr)
        execute_from_command_line(["manage.py", "migrate"])
    except Exception as e:
        print(f"Error running migrations: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Start Gunicorn
    try:
        import gunicorn.app.wsgi
        print("Starting Gunicorn server...", file=sys.stderr)
        
        # Get port from environment variable
        port = int(os.getenv("PORT", "8080"))
        print(f"Using port: {port}", file=sys.stderr)
        
        # Configure Gunicorn
        gunicorn_config = {
            "bind": f"0.0.0.0:{port}",
            "workers": 2,
            "timeout": 300,
            "accesslog": "-",
            "errorlog": "-",
            "loglevel": "info",
            "worker_class": "gthread",
            "threads": 2,
            "keepalive": 5,
            "graceful_timeout": 120,
            "preload_app": True
        }
        
        print("Gunicorn configuration:", file=sys.stderr)
        for key, value in gunicorn_config.items():
            print(f"  {key}: {value}", file=sys.stderr)
        
        # Start Gunicorn
        gunicorn.app.wsgi.run(
            "xblock.wsgi:application",
            **gunicorn_config
        )
    except Exception as e:
        print(f"Error starting Gunicorn: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 