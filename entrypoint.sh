#!/bin/sh
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Verifying demo data..."
python manage.py seed_data || true

echo "==> Starting MediFlow Application on OpenShift..."
exec "$@"
