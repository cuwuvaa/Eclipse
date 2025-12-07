#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Run migrations
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Create default superuser if none exists
python manage.py create_default_superuser

# Collect static files
python manage.py collectstatic --no-input

# Start the application
exec "$@"