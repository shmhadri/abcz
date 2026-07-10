#!/usr/bin/env bash
set -o errexit

echo "==> Installing requirements..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Build finished successfully."
