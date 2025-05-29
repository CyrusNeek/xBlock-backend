#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Log the first 500 characters of BACKEND_ENV for debugging
print("BACKEND_ENV (first 500 chars):", os.environ.get("BACKEND_ENV", "")[:500], file=sys.stderr)

# Load environment variables from BACKEND_ENV if running on Cloud Run
if os.environ.get("K_SERVICE") is not None:
    backend_env = os.environ.get("BACKEND_ENV")
    if backend_env:
        for line in backend_env.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
else:
    try:
        import dotenv
        dotenv.load_dotenv()
        print("Loaded .env for local development", file=sys.stderr)
    except ImportError:
        pass


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
