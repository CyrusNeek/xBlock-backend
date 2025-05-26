#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Load environment variables from .env file
import dotenv
# Note: 'os' module is assumed to be imported prior to this block (it is, at line 2).

# Path for .env file in Cloud Run
cloud_run_env_path = '/app/.env'

if os.path.exists(cloud_run_env_path):
    dotenv.load_dotenv(dotenv_path=cloud_run_env_path)
    print(f"DEBUG: Successfully loaded environment variables from {cloud_run_env_path}")
else:
    # Fallback for local development: try to find .env in the project structure
    # usecwd=True makes it search from the current working directory upwards.
    local_env_path = dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False)
    if local_env_path and os.path.exists(local_env_path):
        dotenv.load_dotenv(local_env_path)
        print(f"DEBUG: Successfully loaded environment variables from {local_env_path} (local fallback)")
    else:
        # This print is important as it indicates a potential configuration issue.
        print("DEBUG: .env file not found at /app/.env or locally. Proceeding without explicit .env loading by this script.")



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
