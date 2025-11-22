#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created successfully.")
else:
    print("Superuser 'admin' already exists.")
EOF

echo "Starting Gunicorn..."
exec gunicorn proj.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2

