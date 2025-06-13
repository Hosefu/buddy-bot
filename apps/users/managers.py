"""
Менеджеры для пользователей
"""
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Менеджер для кастомной модели пользователя
    """

    def _create_user(self, password, **extra_fields):
        """
        Универсальный метод для создания пользователя.
        """
        # Поля 'name' и 'telegram_id' являются обязательными
        if not extra_fields.get('name'):
            raise ValueError('Имя пользователя (name) обязательно')
        if not extra_fields.get('telegram_id'):
            raise ValueError('Telegram ID обязателен')

        # Убираем пробелы из telegram_id
        extra_fields['telegram_id'] = str(extra_fields['telegram_id']).strip()

        # Создаем пользователя
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, name, telegram_id, password=None, **extra_fields):
        """
        Создание обычного пользователя.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        return self._create_user(
            password=password,
            name=name,
            telegram_id=telegram_id,
            **extra_fields
        )

    def create_superuser(self, name, password, **extra_fields):
        """
        Создание суперпользователя.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        # Для суперпользователя, созданного через консоль, генерируем
        # временный уникальный telegram_id, если он не предоставлен.
        if 'telegram_id' not in extra_fields:
            extra_fields['telegram_id'] = f"admin_{int(timezone.now().timestamp())}"
        
        return self._create_user(
            name=name,
            password=password,
            **extra_fields
        )

    def active_users(self):
        """Возвращает только активных пользователей"""
        return self.filter(is_active=True)
    
    def by_telegram_id(self, telegram_id):
        """Поиск пользователя по Telegram ID"""
        return self.filter(telegram_id=str(telegram_id).strip()).first()