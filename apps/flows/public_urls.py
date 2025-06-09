"""
URL для публичных эндпоинтов потоков (/api/flows/)
"""
from django.urls import path
from apps.flows.views import (
    FlowDetailView, FlowStepListView, FlowStepReadView,
    FlowStepTaskView, FlowStepQuizView, QuizQuestionAnswerView
)

urlpatterns = [
    # Детали флоу
    path('<int:pk>/', FlowDetailView.as_view(), name='flow-detail'),
    
    # Этапы флоу
    path('<int:flow_id>/steps/', FlowStepListView.as_view(), name='flow-steps'),
    path('<int:flow_id>/steps/<int:step_id>/read/', FlowStepReadView.as_view(), name='flow-step-read'),
    
    # Контент этапов
    path('<int:flow_id>/steps/<int:step_id>/task/', FlowStepTaskView.as_view(), name='flow-step-task'),
    path('<int:flow_id>/steps/<int:step_id>/quiz/', FlowStepQuizView.as_view(), name='flow-step-quiz'),
    
    # Ответы на квизы
    path('<int:flow_id>/steps/<int:step_id>/quiz/<int:question_id>/', QuizQuestionAnswerView.as_view(), name='quiz-question-answer'),
]