"""
Настройки для продакшена
"""
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Режим отладки отключен
DEBUG = False

# Безопасность
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Доверенные прокси (для корректной работы за load balancer)
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS настройки для продакшена
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

# Настройки базы данных для продакшена
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Кэширование в продакшене
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'onboarding',
        'TIMEOUT': 300,
    }
}

# Сессии в Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Статические файлы и медиа
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # AWS S3 настройки
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Статические файлы в S3
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Медиа файлы в S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Локальное хранение файлов
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = BASE_DIR / 'media'

# Email настройки для продакшена
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Логирование для продакшена
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api_errors': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Celery настройки для продакшена
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 минут
CELERY_TASK_TIME_LIMIT = 600  # 10 минут
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Дополнительные очереди для продакшена
CELERY_TASK_ROUTES.update({
    'apps.users.tasks.send_telegram_notification': {'queue': 'notifications'},
    'apps.flows.tasks.check_overdue_flows': {'queue': 'maintenance'},
    'apps.flows.tasks.generate_daily_statistics': {'queue': 'analytics'},
})

# Мониторинг и ошибки
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style='url'),
            CeleryIntegration(monitor_beat_tasks=True),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment='production',
    )

# Дополнительные настройки безопасности
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='')),
]
MANAGERS = ADMINS

# Настройки для работы с большими данными
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 5   # 5 MB

# Оптимизация запросов
CONN_MAX_AGE = 600

# Дополнительные middleware для продакшена
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статических файлов
] + MIDDLEWARE

# Сжатие статических файлов
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройки для health checks
HEALTH_CHECK_ENABLED = True

# Telegram настройки для продакшена
TELEGRAM_WEBHOOK_URL = config('TELEGRAM_WEBHOOK_URL')
TELEGRAM_MINI_APP_URL = config('TELEGRAM_MINI_APP_URL')

# Дополнительные настройки кэширования
CACHE_TTL = 60 * 15  # 15 минут

# Настройки для работы с файлами
MAX_UPLOAD_SIZE = 1024 * 1024 * 50  # 50 MB

# API rate limiting
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour'
}

# Настройки для мониторинга производительности
SILKY_PYTHON_PROFILER = False  # Отключаем профилировщик в продакшене

# Создаем директории для логов если их нет
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)