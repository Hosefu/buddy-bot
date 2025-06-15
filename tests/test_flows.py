import pytest
from datetime import date, timedelta
from django.utils import timezone
from rest_framework import status

from apps.flows.models import UserFlow, Flow, FlowStep
from apps.common.models import WorkingCalendar

pytestmark = pytest.mark.django_db


@pytest.fixture
def flow_with_steps(flow_factory, flow_step_factory):
    """Фикстура для флоу с несколькими шагами и заданным временем."""
    flow = flow_factory(title="Flow with steps")
    flow_step_factory(flow=flow, title="Step 1")
    flow_step_factory(flow=flow, title="Step 2")
    flow_step_factory(flow=flow, title="Step 3 (inactive)", is_active=False)
    # Итого: 350 минут = 5.83 часа.
    # При 2 часах в день (120 минут), это 350 / 120 = 2.91, округляем вверх до 3 рабочих дней.
    return flow


class TestFlowModel:

    def test_calculate_completion_date_no_steps(self, flow_factory):
        """Тест расчета дедлайна для флоу без шагов."""
        flow = flow_factory()
        start_date = date(2024, 1, 1)  # Понедельник
        # Ожидаем +1 рабочий день, т.к. это минимум
        expected_date = date(2024, 1, 2)
        assert flow.calculate_expected_completion_date(start_date) == expected_date

    def test_calculate_completion_date_with_steps(self, flow_with_steps):
        """Тест расчета дедлайна для флоу с шагами."""
        flow = flow_with_steps
        start_date = date(2024, 1, 1)  # Понедельник
        # 1 рабочий день от 1 января: 2 января.
        expected_date = date(2024, 1, 2)
        assert flow.calculate_expected_completion_date(start_date) == expected_date

    def test_calculate_completion_date_with_holidays(self, flow_with_steps, setup_calendar):
        """Тест расчета с учетом праздников."""
        flow = flow_with_steps
        start_date = date(2024, 1, 5)  # Пятница
        # 1 рабочий день от 5 января -> 9 января (8-е выходной)
        expected_date = date(2024, 1, 9)
        assert flow.calculate_expected_completion_date(start_date) == expected_date


class TestFlowStartApi:

    def test_start_flow_no_deadline_calculates_auto(self, api_client, buddy_user, user, flow_with_steps):
        """
        POST start без deadline: код 201, дедлайн рассчитывается автоматически.
        Этот тест заменяет старый test_b_init_04.
        """
        assert not UserFlow.objects.filter(user=user, flow=flow_with_steps).exists()
        
        data = {'user_id': user.id}

        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{flow_with_steps.id}/start/', data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert UserFlow.objects.filter(user=user, flow=flow_with_steps).exists()
        
        user_flow = UserFlow.objects.get(user=user, flow=flow_with_steps)
        
        # Проверяем, что дата рассчитана и она не None
        assert user_flow.expected_completion_date is not None
        
        # Проверяем, что дата совпадает с расчетом из модели
        expected_date = flow_with_steps.calculate_expected_completion_date(timezone.now().date())
        assert user_flow.expected_completion_date == expected_date

    def test_start_flow_with_deadline_uses_provided(self, api_client, buddy_user, user, simple_flow):
        """
        POST start с указанным deadline: код 201, используется указанный дедлайн.
        Этот тест аналогичен старому test_b_init_03.
        """
        deadline = date.today() + timedelta(days=25)
        data = {
            'user_id': user.id,
            'expected_completion_date': deadline.isoformat()
        }

        api_client.force_authenticate(user=buddy_user)
        response = api_client.post(f'/api/buddy/flows/{simple_flow.id}/start/', data=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        user_flow = UserFlow.objects.get(user=user, flow=simple_flow)
        assert user_flow.expected_completion_date == deadline 