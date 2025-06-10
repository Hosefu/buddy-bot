"""
Общие разрешения для системы онбординга
"""
from rest_framework import permissions
from django.db import models


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его владельцу
    Остальные пользователи могут только читать
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешения на запись только для владельца
        return hasattr(obj, 'user') and obj.user == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его автору
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешения на запись только для автора
        return hasattr(obj, 'author') and obj.author == request.user


class HasRole(permissions.BasePermission):
    """
    Базовое разрешение для проверки роли пользователя
    """
    required_roles = []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Если роли не указаны, разрешаем доступ всем аутентифицированным
        if not self.required_roles:
            return True
        
        # Проверяем наличие любой из требуемых ролей
        return any(
            request.user.has_role(role) for role in self.required_roles
        )


class IsModerator(HasRole):
    """
    Разрешение только для модераторов
    """
    required_roles = ['moderator']


class IsBuddy(HasRole):
    """
    Разрешение только для бадди
    """
    required_roles = ['buddy']


class IsBuddyOrModerator(HasRole):
    """
    Разрешение для бадди или модераторов
    """
    required_roles = ['buddy', 'moderator']


class IsUser(HasRole):
    """
    Разрешение для обычных пользователей
    """
    required_roles = ['user']


class IsActiveUser(permissions.BasePermission):
    """
    Разрешение только для активных пользователей
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


class CanManageFlow(permissions.BasePermission):
    """
    Разрешение для управления потоком обучения
    Модераторы могут управлять всеми потоками
    Бадди могут управлять только назначенными им потоками
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            request.user.has_role('moderator') or
            request.user.has_role('buddy')
        )
    
    def has_object_permission(self, request, view, obj):
        # Модераторы могут управлять всеми потоками
        if request.user.has_role('moderator'):
            return True
        
        # Бадди могут управлять только назначенными им потоками
        if request.user.has_role('buddy'):
            # Проверяем, является ли пользователь бадди для этого потока
            if hasattr(obj, 'flow_buddies'):
                return obj.flow_buddies.filter(
                    buddy_user=request.user,
                    is_active=True
                ).exists()
            
            # Для UserFlow проверяем через связанных бадди
            if hasattr(obj, 'user_flow'):
                return obj.user_flow.flow_buddies.filter(
                    buddy_user=request.user,
                    is_active=True
                ).exists()
        
        return False


class CanViewUserProgress(permissions.BasePermission):
    """
    Разрешение для просмотра прогресса пользователя
    Пользователи могут видеть только свой прогресс
    Бадди могут видеть прогресс своих подопечных
    Модераторы могут видеть прогресс всех пользователей
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Пользователь может видеть свой прогресс
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Модераторы могут видеть прогресс всех
        if request.user.has_role('moderator'):
            return True
        
        # Бадди могут видеть прогресс своих подопечных
        if request.user.has_role('buddy'):
            if hasattr(obj, 'flow_buddies'):
                return obj.flow_buddies.filter(
                    buddy_user=request.user,
                    is_active=True
                ).exists()
        
        return False


class CanEditArticle(permissions.BasePermission):
    """
    Разрешение для редактирования статей
    Авторы могут редактировать свои статьи
    Модераторы могут редактировать любые статьи
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Только для небезопасных методов
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Модераторы могут редактировать любые статьи
        if request.user.has_role('moderator'):
            return True
        
        # Авторы могут редактировать свои статьи
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        return False


class CanPublishArticle(permissions.BasePermission):
    """
    Разрешение для публикации статей
    Только модераторы могут публиковать статьи
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('moderator')
        )


class CanAccessFlowStep(permissions.BasePermission):
    """
    Разрешение для доступа к этапу потока
    Проверяет, доступен ли этап пользователю в рамках его прохождения потока
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Модераторы и бадди имеют доступ ко всем этапам
        if request.user.has_role('moderator') or request.user.has_role('buddy'):
            return True
        
        # Для обычных пользователей проверяем доступность этапа
        if hasattr(view, 'get_user_flow'):
            user_flow = view.get_user_flow()
            if user_flow and user_flow.user == request.user:
                # Проверяем, доступен ли этап
                from apps.flows.models import UserStepProgress
                try:
                    step_progress = UserStepProgress.objects.get(
                        user_flow=user_flow,
                        flow_step=obj
                    )
                    return step_progress.is_accessible
                except UserStepProgress.DoesNotExist:
                    return False
        
        return False


class TelegramBotPermission(permissions.BasePermission):
    """
    Разрешение для Telegram бота
    Проверяет, что запрос исходит от авторизованного бота
    """
    
    def has_permission(self, request, view):
        # Простая проверка по заголовку (в продакшене нужна более сложная логика)
        bot_token = request.META.get('HTTP_X_TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return False
        
        from django.conf import settings
        return bot_token == settings.TELEGRAM_BOT_TOKEN


class CanManageUserRoles(permissions.BasePermission):
    """
    Разрешение для управления ролями пользователей
    Только модераторы могут назначать и отзывать роли
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.has_role('moderator')
        )


class ReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение только на чтение
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS