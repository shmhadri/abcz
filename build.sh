#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🔄 Running migrations..."
python manage.py migrate

echo "📚 Populating CVC data..."
python manage.py populate_all_cvc

echo "🥅 Populating Top Goal data..."
python manage.py populate_topgoal_unit5

echo "✅ Build completed successfully!"
