"""
Конфигурация приложения потоков обучения
"""
from django.apps import AppConfig


class FlowsConfig(AppConfig):
    """
    Конфигурация приложения flows
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.flows'
    verbose_name = 'Потоки обучения'
    
    def ready(self):
        """
        Выполняется при инициализации приложения
        Импортируем сигналы и регистрируем обработчики
        """
        try:
            import apps.flows.signals
        except ImportError:
            pass