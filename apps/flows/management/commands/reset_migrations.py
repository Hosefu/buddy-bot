"""
Команда для пересоздания миграций
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Удаляет все существующие миграции и создает новые'

    def handle(self, *args, **options):
        # Путь к директории с миграциями
        migrations_dir = os.path.join('apps', 'flows', 'migrations')
        
        # Удаляем все файлы миграций, кроме __init__.py
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
                    self.stdout.write(f'Удален файл: {file_path}')
        
        # Создаем новые миграции
        self.stdout.write('Создаем новые миграции...')
        call_command('makemigrations', 'flows')
        
        self.stdout.write(self.style.SUCCESS('Миграции успешно пересозданы!')) 