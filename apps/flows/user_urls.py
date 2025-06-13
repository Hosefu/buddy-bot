"""
URL для пользовательских эндпоинтов (/api/my/)
"""
from django.urls import path
from apps.flows.views import (
    MyFlowListView, MyFlowProgressView
)

# Не используем app_name, т.к. это вложенный urls.py

urlpatterns = [
    # Список и прогресс
    path('flows/', MyFlowListView.as_view(), name='my-flows'),
    path('progress/', MyFlowListView.as_view(), name='my-progress'),  # Ошибка
    path('progress/<int:pk>/', MyFlowProgressView.as_view(), name='my-flow-progress'),
]
