#!/usr/bin/env bash
set -o errexit

echo "==> Installing requirements..."
pip install -r requirements.txt

RUN_MIGRATIONS="${RUN_MIGRATIONS_ON_BUILD:-false}"
case "$(printf '%s' "$RUN_MIGRATIONS" | tr '[:upper:]' '[:lower:]')" in
  1|true|yes|on)
    echo "==> Running database migrations..."
    python manage.py migrate --noinput
    ;;
  *)
    echo "==> Skipping database migrations during build."
    ;;
esac

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Build finished successfully."
