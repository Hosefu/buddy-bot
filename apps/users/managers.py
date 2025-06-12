"""
Менеджеры для пользователей
"""
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """
    Менеджер для кастомной модели пользователя с telegram_id вместо email
    """
    
    def create_user(self, telegram_id, name, password=None, **extra_fields):
        """
        Создание обычного пользователя
        """
        if not telegram_id:
            raise ValueError('Telegram ID обязателен')
        if not name:
            raise ValueError('Имя пользователя обязательно')
        
        # Нормализуем telegram_id (убираем пробелы)
        telegram_id = str(telegram_id).strip()
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(
            telegram_id=telegram_id,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, telegram_id, name, password=None, **extra_fields):
        """
        Создание суперпользователя
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
        
        return self.create_user(telegram_id, name, password, **extra_fields)
    
    def active_users(self):
        """Возвращает только активных пользователей"""
        return self.filter(is_active=True)
    
    def by_telegram_id(self, telegram_id):
        """Поиск пользователя по Telegram ID"""
        return self.filter(telegram_id=telegram_id).first()