#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🔄 Running migrations..."
python manage.py migrate

# ===================================================
# 🔒 PRODUCTION-SAFE DATA SEEDING
# ===================================================
# Only run seeding commands if SEED_DATA environment variable is set
# This prevents accidental data deletion in production
# 
# Usage in development:
#   SEED_DATA=true ./build.sh
# 
# Usage in production (first time only):
#   SEED_DATA=true python manage.py populate_all_cvc
#   SEED_DATA=true python manage.py populate_topgoal_unit5
# ===================================================

if [ "$SEED_DATA" = "true" ]; then
    echo "🌱 SEED_DATA=true detected. Running data population commands..."
    
    echo "📚 Populating CVC data..."
    python manage.py populate_all_cvc
    
    echo "🥅 Populating Top Goal data..."
    python manage.py populate_topgoal_unit5
    
    echo "✅ Data seeding completed!"
else
    echo "⏭️  Skipping data population (SEED_DATA not set)"
    echo "💡 To populate data, run: SEED_DATA=true ./build.sh"
    echo "💡 Or run manually: python manage.py populate_all_cvc"
fi

echo ""
echo "✅ Build completed successfully!"
