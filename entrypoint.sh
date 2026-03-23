#!/bin/sh
set -e

echo "In entrypoint.sh"

DB_FILE="data/db.sqlite3"

if [ ! -f "$DB_FILE" ]; then
    echo "Create DB"
    uv run python manage.py migrate --noinput

    if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo "Create Superuser..."
        uv run python manage.py createsuperuser \
            --noinput \
            --username "$DJANGO_SUPERUSER_USERNAME" \
            --email "$DJANGO_SUPERUSER_EMAIL" || true
    fi

else
    echo "Found db"
fi
echo "Sync db"
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
uv run python manage.py compilemessages

exec "$@"
