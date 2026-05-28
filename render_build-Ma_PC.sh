#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations and collect static
cd backend
python manage.py collectstatic --no-input

# Try to create postgis extension if it doesn't exist
# This requires the database user to have superuser or create extension privileges
python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis;')" || true

python manage.py migrate
