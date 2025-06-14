import pytest
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from apps.flows.models import UserFlow, Flow, FlowBuddy
from apps.users.models import User, Role

pytestmark = pytest.mark.django_db

class TestBuddyApi:
    """
    Тесты для API бадди.
    """

    # --- Section 6: Buddy - инициация флоу ---

    def test_b_init_01_get_buddy_flows(self, api_client, buddy_user, flow_factory):
        """B-INIT-01: GET /api/buddy/flows/ — только is_active=true."""
        flow_factory(title="Active Flow", is_active=True)
        flow_factory(title="Inactive Flow", is_active=False)

        api_client.force_authenticate(user=buddy_user)
        response = api_client.get('/api/buddy/flows/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['is_active'] is True

    def test_b_init_02_get_buddy_users(self, api_client, buddy_user, user_factory):
        """B-INIT-02: GET /api/buddy/users/ — список всех активных пользователей."""
        active = user_factory(telegram_id='active_user_for_buddy', name='Active User', is_active=True)
        inactive = user_factory(telegram_id='inactive_user_for_buddy', name='Inactive User', is_active=False)

        api_client.force_authenticate(user=buddy_user)
        response = api_client.get('/api/buddy/users/')

        assert response.status_code == status.HTTP_200_OK
        
        telegram_ids = [u['telegram_id'] for u in response.data['results']]
        assert active.telegram_id in telegram_ids
        assert inactive.telegram_id not in telegram_ids

    def test_b_init_03_start_flow_for_user(self, api_client, buddy_user, user, simple_flow):
        """B-INIT-03: POST start с валидными user_id + дедлайном → 201, создаётся UserFlow."""
        assert not UserFlow.objects.filter(user=user, flow=simple_flow).exists()
        
        deadline = date.today() + timedelta(days=14)
        data = {
            'user_id': user.id,
            'expected_completion_date': deadline.isoformat()
        }

        api_client.force_authenticate(user=buddy_user)
        # URL из buddy_urls.py: /api/buddy/flows/<int:pk>/start/
        response = api_client.post(f'/api/buddy/flows/{simple_flow.id}/start/', data=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert UserFlow.objects.filter(user=user, flow=simple_flow).exists()
        user_flow = UserFlow.objects.get(user=user, flow=simple_flow)
        assert user_flow.status == UserFlow.FlowStatus.IN_PROGRESS
        assert user_flow.expected_completion_date == deadline
        # Проверка создания FlowAction не реализована, т.к. требует более глубокого анализа.

    def test_b_init_04_start_flow_no_deadline(self, api_client, buddy_user, user, simple_flow):
        """B-INIT-04: POST start без deadline → 400."""
        # Сериализатор UserFlowStartSerializer не делает deadline обязательным.
        # ТЗ говорит - 400. Проверим, как по факту.
        # Если тест провалится - это расхождение с ТЗ.
        data = {'user_id': user.id}
        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{simple_flow.id}/start/', data=data)

        # Ожидаем 201, если поле не обязательное, или 400, если обязательное.
        # Судя по serializers.py `expected_completion_date = serializers.DateField(required=False)`
        # Значит, код будет 201. Оставляем 400, чтобы подсветить расхождение.
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_b_init_05_start_flow_already_active(self, api_client, buddy_user, user, simple_flow, user_flow_factory):
        """B-INIT-05: POST start для уже активного потока того же пользователя → 409."""
        user_flow_factory(user=user, flow=simple_flow, status=UserFlow.FlowStatus.IN_PROGRESS)
        
        data = {
            'user_id': user.id,
            'expected_completion_date': (date.today() + timedelta(days=10)).isoformat()
        }
        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{simple_flow.id}/start/', data=data)

        assert response.status_code == status.HTTP_409_CONFLICT

    # --- Section 7: Buddy - управление ---
    
    @pytest.fixture
    def managed_user_flow(self, user, buddy_user, simple_flow, user_flow_factory):
        """Фикстура для UserFlow, которым управляет buddy_user."""
        user_flow = user_flow_factory(user=user, flow=simple_flow, status=UserFlow.FlowStatus.IN_PROGRESS)
        FlowBuddy.objects.create(user_flow=user_flow, buddy_user=buddy_user)
        return user_flow

    def test_b_mgmt_01_get_my_managed_flows(self, api_client, buddy_user, managed_user_flow):
        """B-MGMT-01: GET /api/buddy/my-flows/ — только те, где текущий пользователь — buddy."""
        api_client.force_authenticate(user=buddy_user)
        response = api_client.get('/api/buddy/my-flows/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == managed_user_flow.id

    def test_b_mgmt_02_get_ward_progress(self, api_client, buddy_user, managed_user_flow):
        """B-MGMT-02: GET /api/buddy/flows/{pid} — подробный прогресс подопечного."""
        api_client.force_authenticate(user=buddy_user)
        # pid - это id UserFlow
        response = api_client.get(f'/api/buddy/flows/{managed_user_flow.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == managed_user_flow.id
        assert 'step_progress' in response.data # Проверяем наличие детального прогресса

    def test_b_mgmt_03_pause_flow(self, api_client, buddy_user, managed_user_flow):
        """B-MGMT-03: POST pause — переводит UserFlow.status в paused."""
        assert managed_user_flow.status == UserFlow.FlowStatus.IN_PROGRESS
        
        api_client.force_authenticate(user=buddy_user)
        # Используем managed_user_flow.id, так как в buddy_urls.py pk - это id UserFlow
        response = api_client.post(f'/api/buddy/flows/{managed_user_flow.id}/pause/', {'reason': 'test pause'})
        
        assert response.status_code == status.HTTP_200_OK
        managed_user_flow.refresh_from_db()
        assert managed_user_flow.status == UserFlow.FlowStatus.PAUSED
        assert managed_user_flow.paused_by == buddy_user
        assert managed_user_flow.paused_at is not None

    def test_b_mgmt_04_resume_flow(self, api_client, buddy_user, managed_user_flow):
        """B-MGMT-04: POST resume — восстанавливает статус."""
        managed_user_flow.status = UserFlow.FlowStatus.PAUSED
        managed_user_flow.paused_by = buddy_user
        managed_user_flow.save()
        
        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{managed_user_flow.id}/resume/')
        
        assert response.status_code == status.HTTP_200_OK
        managed_user_flow.refresh_from_db()
        assert managed_user_flow.status == UserFlow.FlowStatus.IN_PROGRESS

    def test_b_mgmt_05_delete_flow(self, api_client, buddy_user, managed_user_flow):
        """B-MGMT-05: DELETE flow — удаляет UserFlow."""
        user_flow_id = managed_user_flow.id
        assert UserFlow.objects.filter(id=user_flow_id).exists()
        
        api_client.force_authenticate(user=buddy_user)
        response = api_client.delete(f'/api/buddy/flows/{user_flow_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Проверяем, что объект помечен как удаленный (soft-delete)
        assert not UserFlow.objects.active().filter(id=user_flow_id).exists()

    def test_b_mgmt_06_pause_foreign_flow(self, api_client, buddy_user, user, simple_flow, user_flow_factory):
        """B-MGMT-06: Buddy не может паузить чужой поток → 403."""
        # Создаем поток, где buddy_user не является бадди
        foreign_flow = user_flow_factory(user=user, flow=simple_flow)
        
        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{foreign_flow.id}/pause/')
        
        # Ожидаем 403, так как CanManageFlow пермишен не должен пройти
        assert response.status_code == status.HTTP_403_FORBIDDEN 