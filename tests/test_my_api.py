import pytest
from rest_framework import status
from apps.flows.models import UserFlow, Flow, UserStepProgress

pytestmark = pytest.mark.django_db

class TestMyApi:
    """
    Тесты для эндпоинтов /api/my/
    """

    def test_my_01_get_my_flows_unauthorized(self, api_client):
        """
        MY-01: GET /api/my/flows/ - неавторизованный пользователь получает 401
        """
        response = api_client.get('/api/my/flows/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_01_get_my_flows_list(self, api_client, user, user_flow_factory, flow_factory):
        """
        MY-01: GET /api/my/flows/ — список только активных Flow, к которым пользователь назначен
        """
        # Потоки, назначенные пользователю
        active_flow = flow_factory(title="Active Assigned Flow", is_active=True)
        inactive_flow = flow_factory(title="Inactive Assigned Flow", is_active=False)
        user_flow_factory(user=user, flow=active_flow, status=UserFlow.FlowStatus.IN_PROGRESS)
        user_flow_factory(user=user, flow=inactive_flow)

        # Поток, не назначенный пользователю
        flow_factory(title="Unassigned Flow", is_active=True)

        api_client.force_authenticate(user=user)
        response = api_client.get('/api/my/flows/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['flow']['title'] == "Active Assigned Flow"

    def test_my_02_get_my_progress_aggregated(self, api_client, user, flow_factory, flow_step_factory, user_flow_factory):
        """
        MY-02: GET /api/my/progress/ — корректный агрегированный прогресс (percent)
        """
        # --- Flow 1: 2 шага, 1 завершен (50%) ---
        flow1 = flow_factory(title="Flow 1")
        step1_1 = flow_step_factory(flow1, order=1)
        step1_2 = flow_step_factory(flow1, order=2)
        uf1 = user_flow_factory(user=user, flow=flow1, status=UserFlow.FlowStatus.IN_PROGRESS)
        # Сигнал создаст прогресс, нам нужно его обновить
        UserStepProgress.objects.filter(user_flow=uf1, flow_step=step1_1).update(status=UserStepProgress.StepStatus.COMPLETED)
        
        # --- Flow 2: 1 шаг, завершен (100%) ---
        flow2 = flow_factory(title="Flow 2")
        step2_1 = flow_step_factory(flow2, order=1)
        uf2 = user_flow_factory(user=user, flow=flow2, status=UserFlow.FlowStatus.IN_PROGRESS)
        UserStepProgress.objects.filter(user_flow=uf2, flow_step=step2_1).update(status=UserStepProgress.StepStatus.COMPLETED)
        # Завершаем весь флоу, чтобы он считался completed
        uf2.complete()
        uf2.save()

        api_client.force_authenticate(user=user)
        response = api_client.get('/api/my/progress/')

        assert response.status_code == status.HTTP_200_OK
        # 1 активный + 1 завершенный
        assert response.data['total_flows'] == 2
        assert response.data['completed_flows'] == 1
        assert response.data['in_progress_flows'] == 1
        # 50% + 100% / 2 = 75%
        assert response.data['average_progress'] == 75.0

    def test_my_03_get_progress_for_my_flow(self, api_client, user, user_flow_factory, simple_flow):
        """
        MY-03: GET /api/my/progress/{flow_id}/ — 200, если пользователь участвует
        """
        user_flow = user_flow_factory(user=user, flow=simple_flow)

        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/my/progress/{user_flow.flow.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user_flow.id

    def test_my_03_get_progress_for_other_flow(self, api_client, user, another_user, user_flow_factory, simple_flow):
        """
        MY-03: GET /api/my/progress/{flow_id}/ — 404, если пользователь не участвует
        """
        # Поток назначен другому пользователю
        other_user_flow = user_flow_factory(user=another_user, flow=simple_flow)

        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/my/progress/{other_user_flow.flow.id}/')

        # Ожидаем 404, так как UserFlow для этого пользователя и потока не будет найден
        assert response.status_code == status.HTTP_404_NOT_FOUND 