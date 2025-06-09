"""
URL для административных функций (/api/admin/)
"""
from django.urls import path
from apps.flows.views import (
    AdminFlowListView, AdminFlowDetailView, AdminFlowStepListView,
    AdminFlowStepDetailView, AdminAnalyticsOverviewView,
    flow_statistics, problem_users_report
)

urlpatterns = [
    # Управление флоу
    path('flows/', AdminFlowListView.as_view(), name='admin-flows'),
    path('flows/<int:pk>/', AdminFlowDetailView.as_view(), name='admin-flow-detail'),
    
    # Управление этапами флоу
    path('flows/<int:flow_id>/steps/', AdminFlowStepListView.as_view(), name='admin-flow-steps'),
    path('steps/<int:pk>/', AdminFlowStepDetailView.as_view(), name='admin-step-detail'),
    
    # Аналитика и отчеты
    path('analytics/overview/', AdminAnalyticsOverviewView.as_view(), name='admin-analytics-overview'),
    path('analytics/flows/', flow_statistics, name='admin-analytics-flows'),
    path('analytics/users/', flow_statistics, name='admin-analytics-users'),  # Алиас
    path('reports/completion/', flow_statistics, name='admin-reports-completion'),  # Алиас
    path('reports/problems/', problem_users_report, name='admin-reports-problems'),
]