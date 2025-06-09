"""
Настройки для тестирования
"""
from .base import *

# Режим отладки для тестов
DEBUG = True

# Тестовая база данных в памяти для скорости
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Отключаем миграции для скорости тестов
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Простое кэширование для тестов
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Синхронное выполнение Celery задач в тестах
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Отключаем реальные HTTP запросы в тестах
TELEGRAM_BOT_TOKEN = 'test-token'
TELEGRAM_WEBHOOK_URL = 'http://testserver/api/webhook/telegram/'

# Простой email backend для тестов
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Отключаем логирование в файлы для тестов
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Отключаем CORS проверки в тестах
CORS_ALLOW_ALL_ORIGINS = True

# Простые пароли для тестов
AUTH_PASSWORD_VALIDATORS = []

# Статические файлы в памяти
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Отключаем throttling в тестах
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Отключаем проверки безопасности
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Секретный ключ для тестов
SECRET_KEY = 'test-secret-key-not-for-production'

# Разрешенные хосты для тестов
ALLOWED_HOSTS = ['*']

# Отключаем Sentry в тестах
SENTRY_DSN = ''

# Ускоряем хеширование паролей в тестах
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]