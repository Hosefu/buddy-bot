"""
Основная URL конфигурация для приложения users
"""
from django.urls import path, include

from .webhook_urls import urlpatterns as webhook_urlpatterns
from .bot_urls import urlpatterns as bot_urlpatterns

# Импортируем основные URL-шаблоны из модуля users
from apps.users.views import (
    TelegramAuthView, CurrentUserView, ProfileView, PasswordChangeView,
    UserListView, UserDetailView, UserRoleAssignView, RoleListView,
    BuddyListView, telegram_mini_app_auth
)

app_name = 'users'

# Основные URL для аутентификации
urlpatterns = [
    # Аутентификация
    path('telegram/', TelegramAuthView.as_view(), name='telegram-auth'),
    path('telegram-simple/', telegram_mini_app_auth, name='telegram-simple-auth'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # Профиль пользователя
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # Управление пользователями
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/role/', UserRoleAssignView.as_view(), name='user-role-assign'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('buddies/', BuddyListView.as_view(), name='buddy-list'),
] 