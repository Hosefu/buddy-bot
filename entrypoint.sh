#!/bin/bash

# Функции для логирования
log() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_warning() {
    echo -e "\033[0;33m[WARNING]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Создание структуры management команд
create_management_structure() {
    # Создаем пути если они не существуют
    mkdir -p apps/common/management/commands
    
    # Создаем пустые файлы __init__.py для корректной структуры пакета
    touch apps/common/__init__.py
    touch apps/common/management/__init__.py
    touch apps/common/management/commands/__init__.py
}

# Начало
log "Начало инициализации..."

# Проверка подключения к PostgreSQL
log "Ожидание доступности PostgreSQL..."
attempt=0
while ! nc -z $DB_HOST $DB_PORT; do
    attempt=$((attempt + 1))
    if [ $attempt -eq 30 ]; then
        log_warning "База данных недоступна, но продолжаем запуск"
        break
    fi
    echo -n "."
    sleep 1
done

# Дополнительная проверка через psql
log "Проверка подключения к базе данных..."
attempt=0
while ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq 15 ]; then
        log_warning "Не удалось подключиться к базе, но продолжаем (возможно база будет создана)"
        break
    fi
    echo -n "."
    sleep 2
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
    
    # Проверка переменной окружения для загрузки демо-данных
    if [ "$LOAD_DEMO_DATA" = "true" ]; then
        log "Загрузка демонстрационных данных..."
        if python manage.py load_demo_data; then
            log_success "Демонстрационные данные загружены успешно"
        else
            log_warning "Ошибка загрузки демонстрационных данных (продолжаем)"
        fi
    fi
    
    # Если это была команда install, завершаем
    if [ "$SERVICE_TYPE" = "install" ]; then
        log_success "Установка завершена. Система готова к работе."
        exit 0
    fi
fi

log "Инициализация завершена."

# Запуск сервиса в зависимости от SERVICE_TYPE
case "$SERVICE_TYPE" in
    web)
        log "Запуск веб-сервера..."
        exec python manage.py runserver 0.0.0.0:8000
        ;;
    celery-worker)
        log "Запуск Celery Worker..."
        exec celery -A onboarding worker --loglevel=info --concurrency=2
        ;;
    celery-beat)
        log "Запуск Celery Beat..."
        exec celery -A onboarding beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    # Добавлены совместимые имена без дефиса для обратной совместимости
    worker)
        log "Запуск Celery Worker..."
        exec celery -A onboarding worker --loglevel=info --concurrency=2
        ;;
    beat)
        log "Запуск Celery Beat..."
        exec celery -A onboarding beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    *)
        log "Запуск пользовательской команды: $@"
        exec "$@"
        ;;
esac