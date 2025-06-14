"""
URL для buddy функционала (/api/buddy/)
"""
from django.urls import path
from apps.flows.views import (
    BuddyFlowListView, BuddyUserListView, BuddyFlowStartView,
    BuddyMyFlowsView, BuddyFlowManageView, BuddyFlowPauseView,
    BuddyFlowResumeView
)

urlpatterns = [
    # Инициация флоу
    path('flows/', BuddyFlowListView.as_view(), name='buddy-flows'),
    path('users/', BuddyUserListView.as_view(), name='buddy-users'),
    path('flows/<int:pk>/start/', BuddyFlowStartView.as_view(), name='buddy-flow-start'),
    
    # Управление запущенными флоу
    path('my-flows/', BuddyMyFlowsView.as_view(), name='buddy-my-flows'),
    path('flows/<int:pk>/', BuddyFlowManageView.as_view(), name='buddy-flow-detail'),
    path('flows/<int:pk>/pause/', BuddyFlowPauseView.as_view(), name='buddy-flow-pause'),
    path('flows/<int:pk>/resume/', BuddyFlowResumeView.as_view(), name='buddy-flow-resume'),
]