#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для логирования
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия важных зависимостей
check_dependencies() {
    command -v nc >/dev/null 2>&1 || { 
        log_warning "netcat не найден, пропускаем проверку сетевых сервисов"
        return 1
    }
    return 0
}

# Ожидание доступности PostgreSQL
wait_for_postgres() {
    if ! check_dependencies; then
        return
    fi

    log "Ожидание доступности PostgreSQL..."
    local attempt=0
    local max_attempts=30
    
    while ! nc -z $DB_HOST $DB_PORT; do
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            log_warning "База данных недоступна, но продолжаем запуск"
            break
        fi
        echo -n "."
        sleep 1
    done
    
    if [ $attempt -lt $max_attempts ]; then
        log_success "PostgreSQL готов к работе!"
    fi
    
    # Небольшая пауза для стабилизации
    sleep 2
}

# Ожидание доступности Redis
wait_for_redis() {
    if [ -z "$REDIS_URL" ]; then
        return
    fi
    
    if ! check_dependencies; then
        return
    fi
    
    log "Проверка доступности Redis..."
    
    # Извлекаем хост и порт из Redis URL
    REDIS_HOST=$(echo $REDIS_URL | sed 's/redis:\/\///g' | cut -d':' -f1)
    REDIS_PORT=$(echo $REDIS_URL | sed 's/redis:\/\///g' | cut -d':' -f2 | cut -d'/' -f1)
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        local attempt=0
        local max_attempts=15
        
        while ! nc -z $REDIS_HOST $REDIS_PORT; do
            attempt=$((attempt + 1))
            if [ $attempt -eq $max_attempts ]; then
                log_warning "Redis недоступен, но продолжаем запуск"
                break
            fi
            echo -n "."
            sleep 1
        done
        
        if [ $attempt -lt $max_attempts ]; then
            log_success "Redis готов к работе!"
        fi
    fi
}

# Запуск Django веб-сервера
run_web_server() {
    log "Запуск Django веб-сервера..."
    
    # Определяем режим (разработка/продакшн)
    if [ "$DEBUG" = "True" ]; then
        python manage.py runserver 0.0.0.0:8000
    else
        gunicorn onboarding.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile -
    fi
}

# Запуск Celery worker
run_celery_worker() {
    log "Запуск Celery worker..."
    celery -A onboarding worker --loglevel=info
}

# Запуск Celery beat
run_celery_beat() {
    log "Запуск Celery beat..."
    celery -A onboarding beat --loglevel=info
}

# Запуск установки системы
run_system_setup() {
    log "Запуск установки системы..."
    python setup.py install
}

# Основная логика entrypoint
log "==================================================================="
log "                  ЗАПУСК СИСТЕМЫ ОНБОРДИНГА                        "
log "==================================================================="

# Ожидание сервисов
wait_for_postgres
wait_for_redis

# Определяем, что запускаем
SERVICE_TYPE=${1:-"web"}

case "$SERVICE_TYPE" in
    "web")
        # Для веб-сервиса выполняем установку и запускаем сервер
        run_system_setup
        run_web_server
        ;;
    "install")
        # Только установка
        run_system_setup
        ;;
    "celery-worker")
        # Запуск Celery worker
        run_celery_worker
        ;;
    "celery-beat")
        # Запуск Celery beat
        run_celery_beat
        ;;
    *)
        # Для неизвестных команд просто пытаемся выполнить
        log "Выполнение неизвестной команды: $SERVICE_TYPE"
        exec "$@"
        ;;
esac

log "Завершение работы"