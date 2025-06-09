"""
Настройки для разработки
"""
from .base import *

# Режим отладки включен
DEBUG = True

# Разрешенные хосты для разработки
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Добавляем Django Debug Toolbar для разработки
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Внутренние IP для Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# CORS настройки для разработки (разрешаем все)
CORS_ALLOW_ALL_ORIGINS = True

# Менее строгие настройки безопасности для разработки
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Упрощенная конфигурация email для разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Дополнительное логирование для разработки
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Настройки для тестирования Telegram Mini App
TELEGRAM_TEST_MODE = True