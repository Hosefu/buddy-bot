import pytest
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User
from apps.flows.models import Flow

pytestmark = pytest.mark.django_db


def log_request(report_data, name, method, url, response, request_body=None):
    try:
        response_data = response.json()
    except Exception:  # pragma: no cover - fallback for non JSON
        response_data = response.content.decode('utf-8')
    report_data.append({
        'name': name,
        'method': method,
        'url': url,
        'request_body': request_body,
        'response_body': response_data,
        'status_code': response.status_code,
    })


def test_e2e_02_full_moderator_flow(api_client: APIClient, admin_user: User, report_data: list):
    """E2E-02: модератор создаёт и управляет потоком и шагами."""
    api_client.force_authenticate(user=admin_user)

    # Создание потока
    flow_data = {
        'title': 'Новый поток',
        'description': 'Описание потока',
    }
    url = '/api/admin/flows/'
    response = api_client.post(url, flow_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    log_request(report_data, 'Создание потока', 'POST', url, response, flow_data)
    flow_id = response.data['id']

    # Добавление шага
    step_data = {
        'title': 'Шаг 1',
        'description': 'Описание шага',
    }
    url = f'/api/admin/flows/{flow_id}/steps/'
    response = api_client.post(url, step_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    log_request(report_data, 'Создание шага', 'POST', url, response, step_data)
    step_id = response.data['id']

    # Редактирование шага
    step_update = {'title': 'Шаг 1.1'}
    url = f'/api/admin/steps/{step_id}/'
    response = api_client.patch(url, step_update, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == step_update['title']
    log_request(report_data, 'Редактирование шага', 'PATCH', url, response, step_update)

    # Удаление шага
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_request(report_data, 'Удаление шага', 'DELETE', url, response)

    # Редактирование потока
    flow_update = {'title': 'Обновленный поток'}
    url = f'/api/admin/flows/{flow_id}/'
    response = api_client.patch(url, flow_update, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == flow_update['title']
    log_request(report_data, 'Редактирование потока', 'PATCH', url, response, flow_update)

    # Удаление потока
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_request(report_data, 'Удаление потока', 'DELETE', url, response)

    # Проверяем, что поток удален
    assert not Flow.objects.filter(id=flow_id).exists()


def test_admin_endpoints_require_moderator(api_client: APIClient, user: User):
    """Обычный пользователь не должен иметь доступ к admin API."""
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/admin/flows/')
    assert response.status_code == status.HTTP_403_FORBIDDEN
