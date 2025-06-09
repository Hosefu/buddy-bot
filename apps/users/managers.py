"""
Менеджеры для моделей пользователей
"""
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User
    Обрабатывает создание пользователей и суперпользователей
    """
    
    def create_user(self, email, name, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя
        
        Args:
            email (str): Email пользователя
            name (str): Полное имя пользователя
            password (str): Пароль
            **extra_fields: Дополнительные поля
            
        Returns:
            User: Созданный пользователь
        """
        if not email:
            raise ValueError('Email обязателен для создания пользователя')
        
        if not name:
            raise ValueError('Имя обязательно для создания пользователя')
        
        # Нормализуем email
        email = self.normalize_email(email)
        
        # Создаем пользователя
        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )
        
        # Устанавливаем пароль (с хешированием)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя
        
        Args:
            email (str): Email суперпользователя
            name (str): Полное имя суперпользователя
            password (str): Пароль
            **extra_fields: Дополнительные поля
            
        Returns:
            User: Созданный суперпользователь
        """
        # Устанавливаем обязательные поля для суперпользователя
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        # Проверяем корректность полей
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
        
        return self.create_user(email, name, password, **extra_fields)
    
    def create_telegram_user(self, telegram_id, name, **extra_fields):
        """
        Создает пользователя на основе данных Telegram
        Используется при первой авторизации через Telegram Mini App
        
        Args:
            telegram_id (str): ID пользователя в Telegram
            name (str): Имя пользователя
            **extra_fields: Дополнительные поля
            
        Returns:
            User: Созданный пользователь
        """
        if not telegram_id:
            raise ValueError('Telegram ID обязателен')
        
        # Генерируем временный email если не передан
        email = extra_fields.pop('email', f'user_{telegram_id}@telegram.temp')
        
        # Создаем пользователя без пароля (авторизация через Telegram)
        user = self.create_user(
            email=email,
            name=name,
            telegram_id=telegram_id,
            **extra_fields
        )
        
        # Устанавливаем неиспользуемый пароль
        user.set_unusable_password()
        user.save(using=self._db)
        
        return user
    
    def get_by_telegram_id(self, telegram_id):
        """
        Получает пользователя по Telegram ID
        
        Args:
            telegram_id (str): ID пользователя в Telegram
            
        Returns:
            User or None: Пользователь или None если не найден
        """
        try:
            return self.get(telegram_id=telegram_id, is_active=True)
        except self.model.DoesNotExist:
            return None
    
    def active_users(self):
        """
        Возвращает QuerySet активных пользователей
        
        Returns:
            QuerySet: Активные пользователи
        """
        return self.filter(is_active=True, is_deleted=False)
    
    def with_role(self, role_name):
        """
        Возвращает пользователей с определенной ролью
        
        Args:
            role_name (str): Название роли
            
        Returns:
            QuerySet: Пользователи с указанной ролью
        """
        return self.active_users().filter(
            user_roles__role__name=role_name,
            user_roles__is_active=True
        ).distinct()
    
    def buddies(self):
        """
        Возвращает всех активных бадди
        
        Returns:
            QuerySet: Пользователи с ролью buddy
        """
        return self.with_role('buddy')
    
    def moderators(self):
        """
        Возвращает всех активных модераторов
        
        Returns:
            QuerySet: Пользователи с ролью moderator
        """
        return self.with_role('moderator')