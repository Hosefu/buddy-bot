"""
Настройки Django для тестового окружения.
Импортируют все основные настройки и переопределяют их для тестов.
"""
from .settings import *

# Используем быструю базу данных в памяти SQLite3 для тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Используем более быстрый хешер паролей для тестов
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Задачи Celery выполняются синхронно, а не через брокер
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True  # Чтобы видеть исключения из задач

# Отключаем дебаг-панель, если она есть
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False,
}

# Упрощаем логирование для тестов
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Можно поставить DEBUG для более детального вывода
    },
}

# Все "отправленные" письма складываются в память, а не уходят наружу
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend' 