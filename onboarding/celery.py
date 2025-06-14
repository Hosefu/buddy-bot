"""
Конфигурация Celery для фоновых задач
"""
import os
from celery import Celery
from django.conf import settings
from django.utils import timezone

# Создаем экземпляр Celery
app = Celery('onboarding')

# Загружаем конфигурацию из настроек Django
# Пространство имен 'CELERY' означает, что все настройки Celery в settings.py
# должны начинаться с CELERY_, например, CELERY_BROKER_URL
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем файлы tasks.py в приложениях Django
app.autodiscover_tasks()

# Конфигурация периодических задач
app.conf.beat_schedule = {
    # Проверка просроченных потоков каждый день в 9:00
    'check-overdue-flows': {
        'task': 'apps.flows.tasks.check_overdue_flows',
        'schedule': 60.0 * 60.0 * 24.0,  # раз в день
        'options': {'queue': 'default'}
    },
    
    # Отправка напоминаний каждые 3 часа в рабочее время
    'send-reminders': {
        'task': 'apps.flows.tasks.send_flow_reminders',
        'schedule': 60.0 * 60.0 * 3.0,  # каждые 3 часа
        'options': {'queue': 'notifications'}
    },
    
    # Очистка старых сессий каждую неделю
    'cleanup-old-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': 60.0 * 60.0 * 24.0 * 7.0,  # раз в неделю
        'options': {'queue': 'maintenance'}
    },
    
    # Генерация статистики каждую ночь в 2:00
    'generate-statistics': {
        'task': 'apps.flows.tasks.generate_daily_statistics',
        'schedule': 60.0 * 60.0 * 24.0,  # раз в день
        'options': {'queue': 'analytics'}
    }
}

# Часовой пояс для планировщика
app.conf.timezone = settings.TIME_ZONE

# Конфигурация очередей
app.conf.task_routes = {
    # Уведомления Telegram
    'apps.users.tasks.send_telegram_notification': {'queue': 'notifications'},
    'apps.flows.tasks.send_flow_*': {'queue': 'notifications'},
    
    # Аналитика и отчеты
    'apps.flows.tasks.generate_*': {'queue': 'analytics'},
    'apps.guides.tasks.update_*': {'queue': 'analytics'},
    
    # Обслуживание системы
    'apps.*.tasks.cleanup_*': {'queue': 'maintenance'},
    'apps.*.tasks.backup_*': {'queue': 'maintenance'},
    
    # Всё остальное в основную очередь
    '*': {'queue': 'default'}
}

# Настройки для отладки
@app.task(bind=True)
def debug_task(self):
    """Отладочная задача"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'


# Обработчик ошибок
@app.task(bind=True)
def error_handler(self, uuid, error, exc, task, args, kwargs):
    """Обработка ошибок в задачах"""
    print(f'Task {task} failed: {error}')
    
    # Логируем ошибку
    import logging
    logger = logging.getLogger('celery')
    logger.error(f'Task {task} failed with error: {error}', extra={
        'task_id': uuid,
        'args': args,
        'kwargs': kwargs,
        'exception': exc
    })
    
    # Здесь можно добавить отправку уведомлений администраторам
    # например, через Telegram или email


# Мониторинг задач
@app.task
def health_check():
    """Проверка здоровья Celery"""
    return {
        'status': 'healthy',
        'timestamp': str(timezone.now()),
        'worker_id': os.environ.get('HOSTNAME', 'unknown')
    }


if __name__ == '__main__':
    app.start()