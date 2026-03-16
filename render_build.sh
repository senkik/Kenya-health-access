#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations and collect static
# We assume we are in the root directory here
cd backend
python manage.py collectstatic --no-input
python manage.py migrate
