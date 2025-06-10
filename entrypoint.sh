#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования с цветами
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Создание необходимых директорий и файлов
create_management_structure() {
    log "Создание структуры Django management команд..."
    
    # Создаем директории
    mkdir -p /app/apps/common/management/commands
    
    # Создаем __init__.py файлы
    touch /app/apps/common/management/__init__.py
    touch /app/apps/common/management/commands/__init__.py
    
    # Создаем setup_system команду если её нет
    if [ ! -f "/app/apps/common/management/commands/setup_system.py" ]; then
        cat > /app/apps/common/management/commands/setup_system.py << 'EOF'
"""
Django команда для первоначальной настройки системы
"""
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Настройка системы: создание ролей, суперпользователя и Celery Beat'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Настройка системы...'))
        
        success_count = 0
        
        # Создание ролей
        if self.create_roles():
            success_count += 1
            
        # Создание суперпользователя  
        if self.create_superuser():
            success_count += 1
            
        # Настройка Celery Beat
        if self.setup_celery_beat():
            success_count += 1
            
        if success_count == 3:
            self.stdout.write(self.style.SUCCESS('🎉 Настройка завершена успешно!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Настройка завершена частично ({success_count}/3)'))

    def create_roles(self):
        try:
            from apps.users.models import Role
            
            roles_data = [
                {'name': 'user', 'display_name': 'Пользователь', 'description': 'Базовая роль'},
                {'name': 'buddy', 'display_name': 'Бадди', 'description': 'Наставник'},
                {'name': 'moderator', 'display_name': 'Модератор', 'description': 'Администратор'}
            ]
            
            created_count = 0
            with transaction.atomic():
                for role_data in roles_data:
                    role, created = Role.objects.get_or_create(
                        name=role_data['name'],
                        defaults={
                            'display_name': role_data['display_name'],
                            'description': role_data['description'],
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f'✅ Создана роль: {role.display_name}')
                        created_count += 1
                    else:
                        self.stdout.write(f'ℹ️ Роль существует: {role.display_name}')
            
            self.stdout.write(f'📊 Создано ролей: {created_count}')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка создания ролей: {e}'))
            return False

    def create_superuser(self):
        try:
            User = get_user_model()
            
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write('ℹ️ Суперпользователь уже существует')
                return True
            
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_name = os.environ.get('ADMIN_NAME', 'Администратор')
            
            superuser = User.objects.create_superuser(
                email=admin_email,
                name=admin_name,
                password=admin_password
            )
            
            # Назначаем роль модератора
            try:
                from apps.users.models import Role, UserRole
                moderator_role = Role.objects.get(name='moderator')
                UserRole.objects.create(user=superuser, role=moderator_role)
                self.stdout.write('✅ Роль "Модератор" назначена')
            except:
                pass
            
            self.stdout.write(self.style.SUCCESS(f'✅ Суперпользователь создан: {admin_email} / {admin_password}'))
            self.stdout.write(self.style.WARNING('⚠️ СМЕНИТЕ ПАРОЛЬ ПОСЛЕ ПЕРВОГО ВХОДА!'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка создания суперпользователя: {e}'))
            return False

    def setup_celery_beat(self):
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            
            # Создаем расписания
            hourly, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)
            daily, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
            
            tasks = [
                {'name': 'Проверка просроченных потоков', 'task': 'apps.flows.tasks.check_overdue_flows', 'interval': daily},
                {'name': 'Отправка напоминаний', 'task': 'apps.flows.tasks.send_flow_reminders', 'interval': hourly},
                {'name': 'Генерация статистики', 'task': 'apps.flows.tasks.generate_daily_statistics', 'interval': daily},
                {'name': 'Очистка сессий', 'task': 'apps.users.tasks.cleanup_expired_sessions', 'interval': daily}
            ]
            
            created_count = 0
            for task_data in tasks:
                task, created = PeriodicTask.objects.get_or_create(
                    name=task_data['name'],
                    defaults={'task': task_data['task'], 'interval': task_data['interval'], 'enabled': True}
                )
                if created:
                    created_count += 1
            
            self.stdout.write(f'📊 Создано задач Celery: {created_count}')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка настройки Celery Beat: {e}'))
            return False
EOF
        log_success "Создана команда setup_system"
    fi
}

# Проверяем доступность PostgreSQL
log "Ожидание готовности PostgreSQL..."
attempt=0
max_attempts=30

while ! nc -z $DB_HOST $DB_PORT; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        log_error "PostgreSQL недоступен после $max_attempts попыток"
        exit 1
    fi
    echo -n "."
    sleep 1
done

log_success "PostgreSQL готов к работе!"

# Ждем дополнительное время для стабилизации
sleep 3

# Проверяем доступность Redis (если используется)
if [ -n "$REDIS_URL" ]; then
    log "Проверка доступности Redis..."
    
    # Извлекаем хост и порт из Redis URL
    REDIS_HOST=$(echo $REDIS_URL | sed 's/redis:\/\///g' | cut -d':' -f1)
    REDIS_PORT=$(echo $REDIS_URL | sed 's/redis:\/\///g' | cut -d':' -f2 | cut -d'/' -f1)
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        attempt=0
        while ! nc -z $REDIS_HOST $REDIS_PORT; do
            attempt=$((attempt + 1))
            if [ $attempt -eq 15 ]; then
                log_warning "Redis недоступен, но продолжаем запуск"
                break
            fi
            echo -n "."
            sleep 1
        done
        
        if [ $attempt -lt 15 ]; then
            log_success "Redis готов к работе!"
        fi
    fi
fi

# Определяем, что запускаем
SERVICE_TYPE=${1:-"web"}

# Если это первый запуск web сервиса или явная установка
if [ "$SERVICE_TYPE" = "web" ] || [ "$SERVICE_TYPE" = "install" ]; then
    log "Запуск установки системы..."
    
    # Создаем структуру management команд
    create_management_structure
    
    # Применяем миграции
    log "Применение миграций базы данных..."
    if python manage.py migrate --noinput; then
        log_success "Миграции применены успешно"
    else
        log_error "Ошибка применения миграций"
        exit 1
    fi
    
    # Собираем статические файлы
    log "Сбор статических файлов..."
    if python manage.py collectstatic --noinput --clear; then
        log_success "Статические файлы собраны"
    else
        log_warning "Ошибка сбора статических файлов (продолжаем)"
    fi
    
    # Настройка системы
    log "Настройка системы (роли, суперпользователь, Celery Beat)..."
    if python manage.py setup_system; then
        log_success "Система настроена успешно"
    else
        log_warning "Ошибка настройки системы (продолжаем)"
    fi
    
    # Если это была команда install, завершаем
    if [ "$SERVICE_TYPE" = "install" ]; then
        log_success "Установка завершена. Система готова к работе."
        exit 0
    fi
fi

log "Инициализация завершена. Запуск приложения..."

# Для web сервиса запускаем Django
if [ "$SERVICE_TYPE" = "web" ]; then
    log "Запуск Django сервера..."
    exec python manage.py runserver 0.0.0.0:8000

# Для Celery worker
elif [ "$SERVICE_TYPE" = "celery-worker" ]; then
    log "Запуск Celery Worker..."
    exec celery -A onboarding worker --loglevel=info --concurrency=2

# Для Celery beat
elif [ "$SERVICE_TYPE" = "celery-beat" ]; then
    log "Запуск Celery Beat..."
    exec celery -A onboarding beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Для других команд
else
    log "Выполнение команды: $*"
    exec "$@"
fi