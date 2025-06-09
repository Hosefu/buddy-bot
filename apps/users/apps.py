"""
Конфигурация приложения пользователей
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Пользователи'
    
    def ready(self):
        """
        Выполняется при инициализации приложения
        Импортируем сигналы и регистрируем обработчики
        """
        try:
            import apps.users.signals
        except ImportError:
            pass