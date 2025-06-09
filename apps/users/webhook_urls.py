"""
URL для webhook эндпоинтов
"""
from django.urls import path
from apps.users.views import TelegramWebhookView

urlpatterns = [
    path('telegram/', TelegramWebhookView.as_view(), name='telegram-webhook'),
]
