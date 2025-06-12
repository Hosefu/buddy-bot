"""
Django команда для генерации тестовых JWT-токенов API
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    """
    Команда для генерации тестовых JWT-токенов API
    """
    help = 'Генерирует тестовые JWT-токены для демонстрационных пользователей'

    def handle(self, *args, **options):
        """
        Основной метод выполнения команды
        """
        self.stdout.write(self.style.SUCCESS('🔑 Генерация тестовых JWT-токенов API...'))
        
        test_users = [
            'buddy@example.com',
            'user@example.com',
            'moderator@example.com',
        ]
        
        for email in test_users:
            try:
                user = User.objects.get(email=email)
                # Генерация токенов
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                self.stdout.write(f'✅ Токены для {email}:')
                self.stdout.write(f'  • Access Token: {access_token[:15]}...')
                self.stdout.write(f'  • Refresh Token: {refresh_token[:15]}...')
                
                # Для отладки можно сохранить токены в файл
                tokens_file = f'tokens_{user.id}.txt'
                with open(tokens_file, 'w') as f:
                    f.write(f'User: {email}\n')
                    f.write(f'Access Token: {access_token}\n')
                    f.write(f'Refresh Token: {refresh_token}\n')
                
                self.stdout.write(f'  • Токены сохранены в файл: {tokens_file}')
                
            except User.DoesNotExist:
                logger.error(f'Пользователь {email} не найден')
                self.stdout.write(self.style.ERROR(f'⚠️ Пользователь {email} не найден'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Генерация токенов завершена'))