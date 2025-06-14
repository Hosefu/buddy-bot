# Это гарантирует, что Celery приложение будет загружено при старте Django
from .celery import app as celery_app

__all__ = ('celery_app',)
