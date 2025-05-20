python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
gunicorn --timeout 240 xblock.wsgi:application --bind 0.0.0.0:8000 --workers 8