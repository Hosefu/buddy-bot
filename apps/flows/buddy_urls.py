"""
URL для buddy функционала (/api/buddy/)
"""
from django.urls import path
from apps.flows.views import (
    BuddyFlowListView, BuddyUserListView, BuddyFlowStartView,
    BuddyMyFlowsView, BuddyFlowDetailView, BuddyFlowPauseView,
    BuddyFlowResumeView, BuddyFlowDeleteView
)

urlpatterns = [
    # Инициация флоу
    path('flows/', BuddyFlowListView.as_view(), name='buddy-flows'),
    path('users/', BuddyUserListView.as_view(), name='buddy-users'),
    path('flows/<int:pk>/start/', BuddyFlowStartView.as_view(), name='buddy-flow-start'),
    
    # Управление запущенными флоу
    path('my-flows/', BuddyMyFlowsView.as_view(), name='buddy-my-flows'),
    path('flow/<int:pk>/', BuddyFlowDetailView.as_view(), name='buddy-flow-detail'),
    path('flow/<int:flow_id>/pause/', BuddyFlowPauseView.as_view(), name='buddy-flow-pause'),
    path('flow/<int:flow_id>/resume/', BuddyFlowResumeView.as_view(), name='buddy-flow-resume'),
    path('flow/<int:pk>/', BuddyFlowDeleteView.as_view(), name='buddy-flow-delete'),
]