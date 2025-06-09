"""
Команда для инициализации системы
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import Role


class Command(BaseCommand):
    """
    Инициализирует базовые данные системы
    """
    help = 'Инициализирует базовые роли и настройки системы'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать роли если они уже существуют'
        )
    
    def handle(self, *args, **options):
        """Выполняет инициализацию"""
        force = options['force']
        
        with transaction.atomic():
            self.stdout.write('Инициализация системы...')
            
            # Создаем базовые роли
            self.create_roles(force)
            
            self.stdout.write(
                self.style.SUCCESS('Инициализация завершена успешно!')
            )
    
    def create_roles(self, force=False):
        """Создает базовые роли"""
        roles_data = [
            {
                'name': 'user',
                'display_name': 'Пользователь',
                'description': 'Базовая роль для всех пользователей системы'
            },
            {
                'name': 'buddy',
                'display_name': 'Бадди',
                'description': 'Наставник для новых сотрудников'
            },
            {
                'name': 'moderator',
                'display_name': 'Модератор',
                'description': 'Администратор системы с полными правами'
            }
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'display_name': role_data['display_name'],
                    'description': role_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"✓ Создана роль: {role.display_name}")
            elif force:
                role.display_name = role_data['display_name']
                role.description = role_data['description']
                role.is_active = True
                role.save()
                self.stdout.write(f"✓ Обновлена роль: {role.display_name}")
            else:
                self.stdout.write(f"- Роль уже существует: {role.display_name}")