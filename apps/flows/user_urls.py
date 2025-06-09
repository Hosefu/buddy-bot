"""
URL для обычных пользователей (/api/my/)
"""
from django.urls import path
from apps.flows.views import (
    MyFlowListView, MyFlowProgressView
)

urlpatterns = [
    # Мои потоки и прогресс
    path('flows/', MyFlowListView.as_view(), name='my-flows'),
    path('progress/', MyFlowListView.as_view(), name='my-progress'),  # Алиас
    path('progress/<int:pk>/', MyFlowProgressView.as_view(), name='my-flow-progress'),
]