#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating default roles..."
python manage.py shell << EOF
from apps.users.models import Role
Role.objects.get_or_create(name='user', defaults={'display_name': 'Пользователь', 'description': 'Базовая роль'})
Role.objects.get_or_create(name='buddy', defaults={'display_name': 'Бадди', 'description': 'Наставник'})
Role.objects.get_or_create(name='moderator', defaults={'display_name': 'Модератор', 'description': 'Администратор'})
print("Roles created")
EOF

exec "$@" 