#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Load environment variables from .env file
import dotenv
# Note: 'os' module is imported at line 2, 'sys' module at line 3.

# Path for .env file in Cloud Run
cloud_run_env_path = '/app/.env'

print(f"DEBUG MANAGE.PY: DJANGO_SETTINGS_MODULE before dotenv: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)

if os.path.exists(cloud_run_env_path):
    dotenv.load_dotenv(dotenv_path=cloud_run_env_path)
    print(f"DEBUG MANAGE.PY: Attempted to load environment variables from {cloud_run_env_path}", file=sys.stderr)
    print(f"DEBUG MANAGE.PY: DJANGO_SETTINGS_MODULE after dotenv load from {cloud_run_env_path}: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
    print(f"DEBUG MANAGE.PY: DATABASE_URL from env after load: {os.environ.get('DATABASE_URL')}", file=sys.stderr)
    print(f"DEBUG MANAGE.PY: SECRET_KEY from env after load: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
else:
    # Fallback for local development
    local_env_path = dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False)
    if local_env_path and os.path.exists(local_env_path):
        dotenv.load_dotenv(local_env_path)
        print(f"DEBUG MANAGE.PY: Attempted to load environment variables from {local_env_path} (local fallback)", file=sys.stderr)
        print(f"DEBUG MANAGE.PY: DJANGO_SETTINGS_MODULE after dotenv load from {local_env_path}: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
        print(f"DEBUG MANAGE.PY: DATABASE_URL from env after local load: {os.environ.get('DATABASE_URL')}", file=sys.stderr)
        print(f"DEBUG MANAGE.PY: SECRET_KEY from env after local load: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
    else:
        print("DEBUG MANAGE.PY: .env file not found at /app/.env or locally. Proceeding without explicit .env loading by this script.", file=sys.stderr)

print(f"DEBUG MANAGE.PY: DJANGO_SETTINGS_MODULE after entire dotenv block: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)



def main():
    """Run administrative tasks."""
    print(f"DEBUG MANAGE.PY (main): DJANGO_SETTINGS_MODULE at start of main: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
    print(f"DEBUG MANAGE.PY (main): DJANGO_SETTINGS_MODULE after setdefault: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
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
