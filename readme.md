# Telegram Mini App для обучения новичков

Корпоративная система онбординга в виде Telegram Mini App для адаптации новых сотрудников.

## 🎯 Возможности

- **Геймифицированные потоки обучения** с этапами, заданиями и квизами
- **Система Buddy** для наставничества новичков
- **Telegram Mini App** для удобного доступа
- **Административная панель** для HR и модераторов
- **Аналитика и отчеты** по прогрессу обучения
- **Статьи и гайды** с системой закладок
- **Автоматические уведомления** в Telegram

## 🏗️ Технологический стек

### Backend
- **Django 4.2** + Django REST Framework
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и очереди
- **Celery** - фоновые задачи и уведомления

### Bot & Frontend
- **Aiogram 3.2** - Telegram Bot API
- **React** - Telegram Mini App (отдельный репозиторий)

### DevOps
- **Docker** + Docker Compose
- **Nginx** - веб-сервер и прокси
- **Gunicorn** - WSGI сервер

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd buddy-bot
```

### 2. Настройка окружения

```bash
# Копируем файл с переменными окружения
cp .env.example .env

# Редактируем .env файл
nano .env
```

### 3. Запуск с Docker Compose

```bash
# Запуск в режиме разработки
docker-compose up -d

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Создание базовых ролей
docker-compose exec web python manage.py shell -c "
from apps.users.models import Role
Role.objects.get_or_create(name='user', defaults={'display_name': 'Пользователь', 'description': 'Базовая роль'})
Role.objects.get_or_create(name='buddy', defaults={'display_name': 'Бадди', 'description': 'Наставник для новичков'})
Role.objects.get_or_create(name='moderator', defaults={'display_name': 'Модератор', 'description': 'Администратор системы'})
"
```

### 4. Проверка работы

- API: http://localhost:8000/api/
- Админка: http://localhost:8000/admin/
- Документация API: http://localhost:8000/api/docs/

## ⚙️ Настройка Telegram Bot

### 1. Создание бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен и добавьте в `.env`:

```env
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

### 2. Настройка Webhook

```bash
# Установка webhook для бота
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/api/webhook/telegram/"}'
```

### 3. Настройка Mini App

1. В BotFather: `/newapp`
2. Укажите URL вашего Mini App
3. Добавьте в `.env`:

```env
TELEGRAM_MINI_APP_URL=https://your-mini-app-domain.com/
```

## 🔧 Локальная разработка

### Без Docker

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
createdb onboarding

# Миграции
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера разработки
python manage.py runserver

# В отдельном терминале - Celery worker
celery -A onboarding worker --loglevel=info

# В третьем терминале - Celery beat
celery -A onboarding beat --loglevel=info
```

### Установка Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Windows
# Скачайте с https://redis.io/download
```

## 📊 Структура базы данных

### Основные сущности

- **User** - пользователи системы
- **Role** - роли (user, buddy, moderator)
- **Flow** - потоки обучения
- **FlowStep** - этапы потоков
- **UserFlow** - прохождение потоков пользователями
- **Article** - статьи и гайды
- **Task** - задания с кодовыми словами
- **Quiz** - квизы с вопросами

### Диаграмма отношений

```
User ─┬─ UserRole ─ Role
      ├─ UserFlow ─┬─ Flow ─ FlowStep ─┬─ Article
      │           └─ UserStepProgress  ├─ Task
      └─ FlowBuddy                     └─ Quiz
```

## 🔐 Система ролей

### User (Пользователь)
- Видит свои назначенные потоки
- Проходит обучение
- Может добавлять статьи в закладки

### Buddy (Бадди/Наставник)
- Может назначать потоки любому пользователю
- Управляет прогрессом подопечных
- Может приостанавливать/возобновлять потоки
- Получает уведомления о проблемах

### Moderator (Модератор)
- Полный доступ к системе
- Создание и редактирование потоков
- Управление пользователями и ролями
- Доступ к аналитике и отчетам

## 📱 API Endpoints

### Аутентификация
```
POST /api/auth/telegram/     # Авторизация через Telegram
GET  /api/auth/me/           # Текущий пользователь
```

### Пользователи
```
GET  /api/my/flows/          # Мои потоки
GET  /api/my/progress/{id}/  # Мой прогресс
```

### Buddy функции
```
GET  /api/buddy/flows/       # Доступные потоки
POST /api/buddy/flows/{id}/start/  # Запуск потока
GET  /api/buddy/my-flows/    # Мои подопечные
```

### Администрирование
```
GET  /api/admin/flows/       # Управление потоками
GET  /api/admin/analytics/   # Аналитика
```

Полная документация: http://localhost:8000/api/docs/

## 🚀 Деплой в продакшен

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Настройка переменных окружения

```bash
# Создание production .env
cp .env.example .env.production

# Важные настройки для продакшена:
# DEBUG=False
# SECRET_KEY=<secure-random-key>
# ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# DB_PASSWORD=<secure-password>
```

### 3. Запуск в продакшене

```bash
# Сборка и запуск
docker-compose -f docker-compose.yml --profile production up -d

# Миграции
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сборка статических файлов
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автообновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📈 Мониторинг и логи

### Просмотр логов

```bash
# Логи Django
docker-compose logs -f web

# Логи Celery
docker-compose logs -f celery

# Логи Nginx
docker-compose logs -f nginx

# Логи базы данных
docker-compose logs -f db
```

### Мониторинг здоровья

```bash
# Health check endpoint
curl http://localhost/health/

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

### Celery мониторинг

```bash
# Статус Celery worker
docker-compose exec celery celery -A onboarding inspect active

# Статистика задач
docker-compose exec celery celery -A onboarding inspect stats
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Тесты с покрытием
coverage run --source='.' manage.py test
coverage report
coverage html

# Тестирование API
python manage.py test apps.flows.tests.test_api
```

## 🔧 Команды управления

### Создание тестовых данных

```bash
# Создание тестового потока
python manage.py shell -c "
from apps.flows.models import Flow, FlowStep
from apps.guides.models import Article
flow = Flow.objects.create(title='Тестовый поток', description='Описание')
article = Article.objects.create(title='Тестовая статья', content='# Заголовок\nСодержание статьи', is_published=True)
FlowStep.objects.create(flow=flow, title='Первый этап', step_type='article', article=article, order=1)
"
```

### Очистка данных

```bash
# Очистка старых логов
python manage.py shell -c "
from apps.flows.models import FlowAction
from datetime import timedelta
from django.utils import timezone
old_actions = FlowAction.objects.filter(performed_at__lt=timezone.now() - timedelta(days=90))
print(f'Удалено {old_actions.count()} старых действий')
old_actions.delete()
"
```

## 🤝 Участие в разработке

1. Форк репозитория
2. Создание ветки: `git checkout -b feature/amazing-feature`
3. Коммит изменений: `git commit -m 'Add amazing feature'`
4. Push в ветку: `git push origin feature/amazing-feature`
5. Создание Pull Request

### Стиль кода

```bash
# Проверка стиля
flake8 apps/
black --check apps/
isort --check-only apps/

# Автоформатирование
black apps/
isort apps/
```

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- 📧 Email: support@yourcompany.com
- 💬 Telegram: @your_support_bot
- 📋 Issues: [GitHub Issues](https://github.com/yourcompany/telegram-onboarding/issues)

## 🙏 Благодарности

- Django команде за отличный фреймворк
- Telegram за Bot API и Mini Apps
- Всем участникам проекта

---

Сделано с ❤️ для лучшего онбординга сотрудников# buddy-bot
