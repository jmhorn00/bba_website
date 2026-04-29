#!/bin/sh
set -e

echo "==> Waiting for PostgreSQL..."
until nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}" 2>/dev/null; do
    printf '.'
    sleep 1
done
echo ""
echo "==> PostgreSQL is ready."

echo "==> Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
