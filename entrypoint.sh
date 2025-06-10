#!/bin/bash

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Проверяем доступность PostgreSQL
log "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
log "PostgreSQL is ready!"

# Ждем немного, чтобы база точно была готова
sleep 2

# Применяем миграции
log "Applying database migrations..."
python manage.py migrate --noinput

# Собираем статические файлы только если они еще не собраны
log "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Создаем базовые роли если их еще нет
log "Creating default roles..."
python manage.py shell << 'EOF'
try:
    from apps.users.models import Role
    
    # Создаем базовые роли
    user_role, created = Role.objects.get_or_create(
        name='user', 
        defaults={
            'display_name': 'Пользователь', 
            'description': 'Базовая роль для всех пользователей'
        }
    )
    if created:
        print("✓ Создана роль: Пользователь")
    
    buddy_role, created = Role.objects.get_or_create(
        name='buddy', 
        defaults={
            'display_name': 'Бадди', 
            'description': 'Наставник для новых сотрудников'
        }
    )
    if created:
        print("✓ Создана роль: Бадди")
    
    moderator_role, created = Role.objects.get_or_create(
        name='moderator', 
        defaults={
            'display_name': 'Модератор', 
            'description': 'Администратор системы с полными правами'
        }
    )
    if created:
        print("✓ Создана роль: Модератор")
        
    print("✓ Инициализация ролей завершена")
    
except Exception as e:
    print(f"⚠ Ошибка при создании ролей: {e}")
    
EOF

log "Initialization completed. Starting application..."

# Запускаем переданную команду
exec "$@"