"""
URL ��� ������� ������������� (/api/my/)
"""
from django.urls import path
from apps.flows.views import (
    MyFlowListView, MyFlowProgressView
)

# �� ��������� app_name, �.�. �� ��� ������ � ������������ urls.py

urlpatterns = [
    # ��� ������ � ��������
    path('flows/', MyFlowListView.as_view(), name='my-flows'),
    path('progress/', MyFlowListView.as_view(), name='my-progress'),  # �����
    path('progress/<int:pk>/', MyFlowProgressView.as_view(), name='my-flow-progress'),
]
