"""
Модели пользователей и ролей системы
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel, ActiveModel
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Кастомная модель пользователя для системы онбординга
    Расширяет стандартную модель Django дополнительными полями для Telegram и HR данных
    """
    # Основные поля пользователя
    email = models.EmailField(
        'Email адрес',
        unique=True,
        help_text='Корпоративный email пользователя'
    )
    name = models.CharField(
        'Полное имя',
        max_length=255,
        help_text='ФИО пользователя'
    )
    
    # Telegram интеграция
    telegram_id = models.CharField(
        'Telegram ID',
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text='Уникальный ID пользователя в Telegram'
    )
    telegram_username = models.CharField(
        'Telegram username',
        max_length=100,
        null=True,
        blank=True,
        help_text='Username пользователя в Telegram (@username)'
    )
    
    # HR информация
    position = models.CharField(
        'Должность',
        max_length=255,
        null=True,
        blank=True,
        help_text='Должность сотрудника в компании'
    )
    department = models.CharField(
        'Отдел',
        max_length=255,
        null=True,
        blank=True,
        help_text='Отдел или департамент'
    )
    hire_date = models.DateField(
        'Дата найма',
        null=True,
        blank=True,
        help_text='Дата поступления на работу'
    )
    
    # Системные поля
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Определяет, может ли пользователь войти в систему'
    )
    is_staff = models.BooleanField(
        'Сотрудник',
        default=False,
        help_text='Определяет доступ к административной панели Django'
    )
    last_login_at = models.DateTimeField(
        'Последний вход',
        null=True,
        blank=True
    )
    
    # Менеджер пользователей
    objects = UserManager()
    
    # Поля для аутентификации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['email']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        return self.name
    
    def get_short_name(self):
        """Возвращает краткое имя пользователя"""
        return self.name.split()[0] if self.name else self.email
    
    @property
    def telegram_link(self):
        """Возвращает ссылку на профиль Telegram"""
        if self.telegram_username:
            return f"https://t.me/{self.telegram_username.lstrip('@')}"
        return None
    
    def has_role(self, role_name):
        """Проверяет, имеет ли пользователь определенную роль"""
        return self.user_roles.filter(
            role__name=role_name,
            is_active=True
        ).exists()
    
    def get_active_roles(self):
        """Возвращает список активных ролей пользователя"""
        return self.user_roles.filter(is_active=True).select_related('role')


class Role(BaseModel, ActiveModel):
    """
    Модель ролей в системе (user, buddy, moderator)
    Определяет уровни доступа пользователей к функционалу
    """
    class RoleChoices(models.TextChoices):
        USER = 'user', 'Пользователь'
        BUDDY = 'buddy', 'Бадди'
        MODERATOR = 'moderator', 'Модератор'
    
    name = models.CharField(
        'Название роли',
        max_length=50,
        choices=RoleChoices.choices,
        unique=True,
        help_text='Системное название роли'
    )
    display_name = models.CharField(
        'Отображаемое название',
        max_length=100,
        help_text='Название роли для отображения пользователям'
    )
    description = models.TextField(
        'Описание',
        help_text='Описание прав и возможностей роли'
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
    
    def __str__(self):
        return self.display_name


class UserRole(BaseModel):
    """
    Связь пользователя с ролью
    Позволяет назначать пользователям множественные роли с историей изменений
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_users',
        verbose_name='Роль'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name='Назначил',
        help_text='Пользователь, который назначил эту роль'
    )
    assigned_at = models.DateTimeField(
        'Дата назначения',
        default=timezone.now,
        help_text='Когда была назначена роль'
    )
    is_active = models.BooleanField(
        'Активна',
        default=True,
        help_text='Активна ли роль в данный момент'
    )
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = [('user', 'role')]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.role.display_name}"


class TelegramSession(BaseModel):
    """
    Модель для хранения сессий Telegram Mini App
    Необходима для валидации запросов от Telegram
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_sessions',
        verbose_name='Пользователь'
    )
    telegram_data = models.JSONField(
        'Данные Telegram',
        help_text='Данные, полученные от Telegram Mini App'
    )
    auth_date = models.DateTimeField(
        'Дата авторизации',
        help_text='Время авторизации в Telegram'
    )
    hash_value = models.CharField(
        'Хеш',
        max_length=64,
        help_text='Хеш для валидации данных'
    )
    is_valid = models.BooleanField(
        'Валидна',
        default=True,
        help_text='Действительна ли сессия'
    )
    expires_at = models.DateTimeField(
        'Истекает',
        help_text='Время истечения сессии'
    )
    
    class Meta:
        db_table = 'telegram_sessions'
        verbose_name = 'Telegram сессия'
        verbose_name_plural = 'Telegram сессии'
        indexes = [
            models.Index(fields=['user', 'is_valid']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Сессия {self.user.name} от {self.auth_date}"
    
    def is_expired(self):
        """Проверяет, истекла ли сессия"""
        return timezone.now() > self.expires_at