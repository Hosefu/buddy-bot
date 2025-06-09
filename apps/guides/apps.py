"""
Конфигурация приложения статей и гайдов
"""
from django.apps import AppConfig


class GuidesConfig(AppConfig):
    """
    Конфигурация приложения guides
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.guides'
    verbose_name = 'Статьи и гайды'
    
    def ready(self):
        """
        Выполняется при инициализации приложения
        Импортируем сигналы и регистрируем обработчики
        """
        try:
            import apps.guides.signals
        except ImportError:
            pass