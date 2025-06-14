"""
Базовые классы для Celery задач
"""
from celery import Task
from django.core.cache import cache
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger('celery.tasks')


class BaseTask(Task):
    """Базовый класс для всех Celery задач"""
    
    # Настройки повторов
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def before_start(self, task_id: str, args: tuple, kwargs: dict):
        """Перед началом выполнения"""
        logger.info(f"Starting task {self.name}[{task_id}]")
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict):
        """При успешном выполнении"""
        logger.info(f"Task {self.name}[{task_id}] completed successfully")
        # Очистка временных данных
        cache.delete(f"task_lock:{task_id}")
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any):
        """При ошибке выполнения"""
        logger.error(
            f"Task {self.name}[{task_id}] failed: {exc}",
            exc_info=True
        )
        # Отправка уведомления об ошибке
        from apps.users.tasks import send_error_notification
        send_error_notification.delay(
            task_name=self.name,
            task_id=task_id,
            error=str(exc)
        )


class SingletonTask(BaseTask):
    """Задача, которая может выполняться только в единственном экземпляре"""
    
    def __call__(self, *args, **kwargs):
        """Проверка на уникальность перед выполнением"""
        lock_key = f"singleton_task:{self.name}"
        
        # Пытаемся установить блокировку
        if cache.add(lock_key, True, timeout=3600):  # 1 час
            try:
                return super().__call__(*args, **kwargs)
            finally:
                cache.delete(lock_key)
        else:
            logger.warning(f"Task {self.name} already running, skipping")
            return None


class PeriodicTask(BaseTask):
    """Задача для периодического выполнения"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = kwargs.get('period', 3600)  # По умолчанию 1 час
    
    def __call__(self, *args, **kwargs):
        """Проверка периода перед выполнением"""
        last_run_key = f"last_run:{self.name}"
        last_run = cache.get(last_run_key)
        
        if last_run is None:
            try:
                result = super().__call__(*args, **kwargs)
                cache.set(last_run_key, True, timeout=self.period)
                return result
            except Exception as e:
                logger.error(f"Error in periodic task {self.name}: {e}")
                return None
        else:
            logger.debug(f"Task {self.name} skipped - too soon")
            return None 