#!/usr/bin/env bash
set -o errexit

echo "==> Installing requirements..."
pip install -r requirements.txt

echo "==> Collecting static..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding CVC data (safe)..."
python manage.py populate_all_cvc || true

echo "==> Seeding TopGoal (safe)..."
python manage.py populate_topgoal_unit5 || true

echo "==> Build finished ✅"
