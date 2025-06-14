import pytest
from rest_framework.test import APIClient
from apps.users.models import User
from apps.flows.models import Flow, UserFlow, UserStepProgress, FlowStep

pytestmark = pytest.mark.django_db

def log_request(report_data, name, method, url, response, request_body=None):
    """Вспомогательная функция для логирования шагов теста."""
    response_data = None
    try:
        response_data = response.json()
    except Exception:
        response_data = response.content.decode('utf-8')

    report_data.append({
        'name': name,
        'method': method,
        'url': url,
        'request_body': request_body,
        'response_body': response_data,
        'status_code': response.status_code,
    })

def test_full_user_flow(
    api_client: APIClient, 
    buddy_user: User, 
    user: User, 
    flow_with_steps: Flow, 
    report_data: list
):
    """
    Тестирует полный жизненный цикл взаимодействия пользователя с системой.
    """
    
    # Шаг 0: Бадди смотрит пользователей всех
    api_client.force_authenticate(user=buddy_user)
    users_url = '/api/buddy/users/'
    response = api_client.get(users_url)
    assert response.status_code == 200, f"Expected 200, got {response.status_code} from {users_url}"
    assert any(u['telegram_id'] == user.telegram_id for u in response.json()['results'])
    log_request(report_data, "Бадди просматривает список пользователей", "GET", users_url, response)

    # Шаг 1: Бадди запускает флоу с пользователем
    start_flow_url = f'/api/buddy/flows/{flow_with_steps.id}/start/'
    request_body = {'user_id': user.id}
    response = api_client.post(start_flow_url, request_body, format='json')
    assert response.status_code == 201, f"Expected 201, got {response.status_code} from {start_flow_url}"
    log_request(report_data, "Бадди назначает флоу пользователю", "POST", start_flow_url, response, request_body)

    user_flow = UserFlow.objects.get(user=user, flow=flow_with_steps)
    
    # Шаг 2: Пользователь смотрит все свои флоу
    api_client.force_authenticate(user=user)
    my_flows_url = '/api/my/flows/'
    response = api_client.get(my_flows_url)
    assert response.status_code == 200, f"Expected 200, got {response.status_code} from {my_flows_url}"
    assert response.json()['count'] > 0
    assert response.json()['results'][0]['id'] == user_flow.id
    log_request(report_data, "Пользователь просматривает свои флоу", "GET", my_flows_url, response)

    # Шаг 3: Пользователь проходит флоу
    progress_url = f'/api/my/progress/{user_flow.flow.id}/'
    
    # Шаг 3.1: Прохождение статьи
    step1 = flow_with_steps.flow_steps.get(step_type=FlowStep.StepType.ARTICLE)
    complete_step_url = f'/api/flows/{flow_with_steps.id}/steps/{step1.id}/read/'
    response = api_client.post(complete_step_url)
    assert response.status_code == 200
    log_request(report_data, "Пользователь завершает шаг со статьей", "POST", complete_step_url, response)

    step1_progress = UserStepProgress.objects.get(user_flow=user_flow, flow_step=step1)
    assert step1_progress.status == UserStepProgress.StepStatus.COMPLETED

    # Шаг 3.2: Прохождение задания
    step2 = flow_with_steps.flow_steps.get(step_type=FlowStep.StepType.TASK)
    submit_task_url = f'/api/flows/{flow_with_steps.id}/steps/{step2.id}/task/'
    task_body = {'answer': 'secret'}
    response = api_client.post(submit_task_url, task_body, format='json')
    assert response.status_code == 200
    assert response.json()['is_correct'] is True
    log_request(report_data, "Пользователь отправляет кодовое слово", "POST", submit_task_url, response, task_body)

    step2_progress = UserStepProgress.objects.get(user_flow=user_flow, flow_step=step2)
    assert step2_progress.status == UserStepProgress.StepStatus.COMPLETED

    # Шаг 3.3: Прохождение квиза
    step3 = flow_with_steps.flow_steps.get(step_type=FlowStep.StepType.QUIZ)
    question = step3.quiz.questions.first()
    correct_answer = question.answers.get(is_correct=True)
    submit_quiz_url = f'/api/flows/{flow_with_steps.id}/steps/{step3.id}/quiz/{question.id}/'
    quiz_body = {'answer_id': correct_answer.id}
    response = api_client.post(submit_quiz_url, quiz_body, format='json')
    assert response.status_code == 200
    assert response.json()['is_correct'] is True
    log_request(report_data, "Пользователь отвечает на квиз", "POST", submit_quiz_url, response, quiz_body)
    
    step3_progress = UserStepProgress.objects.get(user_flow=user_flow, flow_step=step3)
    assert step3_progress.status == UserStepProgress.StepStatus.COMPLETED
    
    # Шаг 4: Проверяем, что флоу завершен
    user_flow.refresh_from_db()
    assert user_flow.status == UserFlow.FlowStatus.COMPLETED
    
    # Делаем финальный запрос для лога
    final_response = api_client.get(progress_url)
    log_request(report_data, "Пользователь проверяет завершение флоу", "GET", progress_url, final_response)
    assert final_response.json()['status'] == 'completed' 