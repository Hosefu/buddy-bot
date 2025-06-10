"""
URL конфигурация для пользователей
"""
from django.urls import path
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    TelegramAuthView, CurrentUserView, ProfileView, PasswordChangeView,
    UserListView, UserDetailView, UserRoleAssignView, RoleListView,
    BuddyListView, telegram_mini_app_auth, TelegramWebhookView, BotUserInfoView
)

app_name = 'users'

# Основные URL для аутентификации
urlpatterns = [
    # Аутентификация
    path('telegram/', TelegramAuthView.as_view(), name='telegram-auth'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # Профиль пользователя
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # Управление пользователями (админ)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Управление ролями
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('users/<int:user_id>/roles/', UserRoleAssignView.as_view(), name='assign-role'),
    path('users/<int:user_id>/roles/<int:role_id>/', UserRoleAssignView.as_view(), name='revoke-role'),
    
    # Список бадди
    path('buddies/', BuddyListView.as_view(), name='buddy-list'),
    
    # Webhook и Bot API
    path('webhook/telegram/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('bot/user/<str:telegram_id>/', BotUserInfoView.as_view(), name='bot-user-info'),
]

# Упрощенный эндпоинт авторизации используется только в режиме разработки
if settings.DEBUG:
    urlpatterns.insert(1, path('telegram-simple/', telegram_mini_app_auth, name='telegram-simple-auth'))
