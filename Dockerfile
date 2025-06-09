# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=onboarding.settings.development

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
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем директории для логов и медиа файлов
RUN mkdir -p /app/logs /app/media /app/staticfiles \
    && chmod -R 777 /app/logs

# Копируем код проекта
COPY . /app/

# Создаем пользователя для запуска приложения
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Устанавливаем права доступа
RUN chown -R django:django /app \
    && chmod -R 777 /app/logs
USER django

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]