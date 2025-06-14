"""
Команда для полного сброса и пересоздания миграций Django.
Удаляет все существующие миграции и создает новые чистые.
Полезно на этапе разработки для решения проблем с миграциями.

Использование:
    python manage.py reset_all_migrations  # Сбросить и пересоздать все миграции

ВНИМАНИЕ: Эту команду следует использовать только в режиме разработки, никогда на продакшене!
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Удаляет все существующие миграции и создает новые чистые (только для разработки)'
    
    def handle(self, *args, **options):
        """Основной метод выполнения команды"""
        # Отключаем проверку базы данных
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

        # Список приложений
        apps_to_reset = [
            'contenttypes', 'auth', 'admin', 'sessions', 
            'django_celery_beat', 'django_celery_results', 
            'users', 'flows', 'guides'
        ]

        # Удаляем существующие миграции
        for app in apps_to_reset:
            migrations_path = f'apps/{app}/migrations' if app not in ['contenttypes', 'auth', 'admin', 'sessions'] else None
            
            if migrations_path and os.path.exists(migrations_path):
                for filename in os.listdir(migrations_path):
                    if filename != '__init__.py':
                        file_path = os.path.join(migrations_path, filename)
                        os.remove(file_path)
                self.stdout.write(f'Очищены миграции для {app}')

        # Создаем новые миграции без применения
        call_command('makemigrations', *apps_to_reset)

        self.stdout.write(self.style.SUCCESS('🎉 Миграции успешно сброшены и пересозданы'))