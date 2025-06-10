"""
Django команда для первоначальной настройки системы
"""
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Настройка системы: создание ролей, суперпользователя и Celery Beat'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Настройка системы...'))
        
        success_count = 0
        
        # Создание ролей
        if self.create_roles():
            success_count += 1
            
        # Создание суперпользователя  
        if self.create_superuser():
            success_count += 1
            
        # Настройка Celery Beat
        if self.setup_celery_beat():
            success_count += 1
            
        if success_count == 3:
            self.stdout.write(self.style.SUCCESS('🎉 Настройка завершена успешно!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Настройка завершена частично ({success_count}/3)'))

    def create_roles(self):
        try:
            from apps.users.models import Role
            
            roles_data = [
                {'name': 'user', 'display_name': 'Пользователь', 'description': 'Базовая роль'},
                {'name': 'buddy', 'display_name': 'Бадди', 'description': 'Наставник'},
                {'name': 'moderator', 'display_name': 'Модератор', 'description': 'Администратор'}
            ]
            
            created_count = 0
            with transaction.atomic():
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
                        self.stdout.write(f'✅ Создана роль: {role.display_name}')
                        created_count += 1
                    else:
                        self.stdout.write(f'ℹ️ Роль существует: {role.display_name}')
            
            self.stdout.write(f'📊 Создано ролей: {created_count}')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка создания ролей: {e}'))
            return False

    def create_superuser(self):
        try:
            User = get_user_model()
            
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write('ℹ️ Суперпользователь уже существует')
                return True
            
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_name = os.environ.get('ADMIN_NAME', 'Администратор')
            
            superuser = User.objects.create_superuser(
                email=admin_email,
                name=admin_name,
                password=admin_password
            )
            
            # Назначаем роль модератора
            try:
                from apps.users.models import Role, UserRole
                moderator_role = Role.objects.get(name='moderator')
                UserRole.objects.create(user=superuser, role=moderator_role)
                self.stdout.write('✅ Роль "Модератор" назначена')
            except:
                pass
            
            self.stdout.write(self.style.SUCCESS(f'✅ Суперпользователь создан: {admin_email} / {admin_password}'))
            self.stdout.write(self.style.WARNING('⚠️ СМЕНИТЕ ПАРОЛЬ ПОСЛЕ ПЕРВОГО ВХОДА!'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка создания суперпользователя: {e}'))
            return False

    def setup_celery_beat(self):
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            
            # Создаем расписания
            hourly, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)
            daily, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
            
            tasks = [
                {'name': 'Проверка просроченных потоков', 'task': 'apps.flows.tasks.check_overdue_flows', 'interval': daily},
                {'name': 'Отправка напоминаний', 'task': 'apps.flows.tasks.send_flow_reminders', 'interval': hourly},
                {'name': 'Генерация статистики', 'task': 'apps.flows.tasks.generate_daily_statistics', 'interval': daily},
                {'name': 'Очистка сессий', 'task': 'apps.users.tasks.cleanup_expired_sessions', 'interval': daily}
            ]
            
            created_count = 0
            for task_data in tasks:
                task, created = PeriodicTask.objects.get_or_create(
                    name=task_data['name'],
                    defaults={'task': task_data['task'], 'interval': task_data['interval'], 'enabled': True}
                )
                if created:
                    created_count += 1
            
            self.stdout.write(f'📊 Создано задач Celery: {created_count}')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка настройки Celery Beat: {e}'))
            return False
