"""
URL для bot API
"""
from django.urls import path
from apps.users.views import BotUserInfoView

urlpatterns = [
    path('user/<str:telegram_id>/', BotUserInfoView.as_view(), name='bot-user-info'),
]
