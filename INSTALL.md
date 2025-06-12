# Руководство по установке системы онбординга

Это руководство описывает процесс установки и настройки системы онбординга.

## Новая система установки

После рефакторинга системы установки, все команды по настройке и управлению проектом были консолидированы в двух основных файлах:

1. `setup.py` - основной скрипт установки и настройки системы
2. `Makefile` - удобный интерфейс для выполнения общих задач

## Быстрый старт

### Через Docker Compose (рекомендуется)

```bash
# Клонирование репозитория
git clone <repository-url>
cd buddy-bot

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл под свои нужды

# Запуск системы
docker-compose up -d

# Установка и настройка системы
make docker-install
```

### Локальная разработка (без Docker)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка системы
python setup.py install

# Запуск сервера разработки
python manage.py runserver
```

## Использование setup.py

`setup.py` - это основной скрипт для установки и настройки системы. Он предоставляет несколько команд:

```bash
# Полная установка системы
python setup.py install

# Только миграции БД
python setup.py migrate

# Сборка статических файлов
python setup.py static

# Создание суперпользователя
python setup.py createsuperuser

# Загрузка демо-данных
python setup.py demo

# Проверка системы
python setup.py check

# Настройка вебхука Telegram
python setup.py setup-webhook

# Справка по командам
python setup.py --help
```

## Использование Makefile

Makefile предоставляет удобные команды для управления проектом:

```bash
# Показать доступные команды
make help

# Полная установка системы
make install

# Запуск системы в режиме разработки
make run

# Остановка системы
make stop

# Применить миграции
make migrate

# Создать суперпользователя
make superuser

# Проверка системы
make check

# Запуск в режиме продакшн
make prod-up
```

Для Docker-окружения используйте команды с префиксом `docker-`:

```bash
# Установка через Docker
make docker-install

# Миграции через Docker
make docker-migrate

# Создание суперпользователя через Docker
make docker-superuser
```

## Структура системы установки

После рефакторинга система установки стала более понятной и однозначной:

- `setup.py` - единая точка входа для всех операций установки
- `entrypoint.sh` - скрипт для Docker-контейнеров, инициализирует окружение и запускает нужные сервисы
- `docker-compose.yml` - конфигурация Docker Compose для запуска всех компонентов системы
- `Makefile` - набор удобных команд для управления проектом

## Переменные окружения

Основные переменные окружения, используемые системой:

```
# Django settings
DJANGO_SETTINGS_MODULE=onboarding.settings
SECRET_KEY=your-secret-key
DEBUG=True  # Измените на False для продакшн
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_NAME=onboarding
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/webhook/telegram/
TELEGRAM_MINI_APP_URL=https://t.me/your_bot/app

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-password
ADMIN_NAME=Администратор

# Demo data
LOAD_DEMO_DATA=true  # Загрузка демо-данных при установке
```

## Запуск в продакшене

Для запуска системы в продакшене используйте профиль production в Docker Compose:

```bash
# Копирование и настройка переменных окружения для продакшн
cp .env.example .env.production
# Отредактируйте .env.production

# Запуск в режиме продакшн
docker-compose --profile production --env-file .env.production up -d

# Или используйте Makefile
make prod-up
```

## Важные заметки

1. В продакшн-окружении обязательно измените следующие параметры:
   - Установите `DEBUG=False`
   - Генерируйте надежный `SECRET_KEY`
   - Установите корректные `ALLOWED_HOSTS`
   - Задайте безопасные пароли для БД и администратора

2. Для работы Telegram Mini App нужно правильно настроить вебхук:
   ```bash
   python setup.py setup-webhook
   ```

3. После установки системы рекомендуется сменить пароль администратора через веб-интерфейс.

## Устранение неполадок

### Проблемы с подключением к базе данных

Убедитесь, что параметры подключения к БД в `.env` файле корректны. Для диагностики используйте:

```bash
make docker-check
```

### Проблемы с Redis

Проверьте доступность Redis:

```bash
docker-compose exec redis redis-cli ping
```

### Логи системы

Для просмотра логов используйте:

```bash
# Все логи
make logs

# Логи конкретного сервиса
make logs-web
make logs-celery
```

## Дополнительная информация

Дополнительную информацию о системе онбординга можно найти в файле README.md.