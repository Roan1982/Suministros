#!/bin/sh
set -e

# Small wait-for-db loop using nc (netcat)
if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
  echo "Waiting for database $DATABASE_HOST:$DATABASE_PORT..."
  while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
    echo "Waiting for postgres..."
    sleep 1
  done
fi

# Run migrations and collectstatic
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files (safe to run in dev also)
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Execute CMD
exec "$@"
