# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=onboarding.settings

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        curl \
        netcat-traditional \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем директории для логов, медиа файлов и статики
RUN mkdir -p /app/logs /app/media /app/staticfiles \
    && chmod -R 755 /app

# Копируем код проекта
COPY . /app/

# Создаем пользователя для запуска приложения (безопасность)
RUN groupadd --system django \
    && useradd --system --gid django --home /app django \
    && chown -R django:django /app \
    && chmod -R 755 /app/logs

# Копируем и настраиваем entrypoint скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открываем порт для Django
EXPOSE 8000

# Используем созданного пользователя
USER django

# Точка входа
ENTRYPOINT ["/entrypoint.sh"]

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]