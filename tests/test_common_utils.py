import pytest
from datetime import date, timedelta
from django.utils import timezone

from apps.common.models import WorkingCalendar
from apps.common.utils import add_working_days, get_working_days_count

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_calendar():
    """Настраивает календарь с несколькими выходными."""
    # Праздник
    WorkingCalendar.objects.create(date=date(2024, 1, 8), is_working_day=False, description="Праздник")
    # Перенесенный рабочий день (суббота)
    WorkingCalendar.objects.create(date=date(2024, 1, 13), is_working_day=True, description="Рабочая суббота")
    # Обычный выходной (воскресенье), который мы не трогаем
    # date(2024, 1, 14)
    # Обычный рабочий день (понедельник), который мы делаем выходным
    WorkingCalendar.objects.create(date=date(2024, 1, 15), is_working_day=False, description="Дополнительный выходной")


class TestWorkingDaysUtils:

    def test_add_working_days_simple(self):
        """Простой тест: добавляем 5 рабочих дней к понедельнику."""
        start_date = date(2024, 1, 1)  # Понедельник
        expected_date = date(2024, 1, 8)  # Следующий понедельник
        result = add_working_days(start_date, 5)
        assert result == expected_date

    def test_add_working_days_across_weekend(self):
        """Тест: добавляем 3 рабочих дня к четвергу."""
        start_date = date(2024, 1, 4)  # Четверг
        expected_date = date(2024, 1, 9)  # Следующий вторник
        result = add_working_days(start_date, 3)
        assert result == expected_date

    def test_add_working_days_with_holidays(self, setup_calendar):
        """Тест: добавление дней с учетом кастомного календаря."""
        start_date = date(2024, 1, 5)  # Пятница
        # Ожидаемый подсчет:
        # 1. 9 янв (вт)
        # 2. 10 янв (ср)
        # 3. 11 янв (чт)
        # 4. 12 янв (пт)
        # 5. 13 янв (сб - рабочий)
        # 8 янв - выходной, 14 янв - выходной, 15 янв - выходной
        expected_date = date(2024, 1, 16) # Вторник
        result = add_working_days(start_date, 6)
        assert result == expected_date

    def test_add_zero_or_negative_days(self):
        start_date = date(2024, 1, 10)
        assert add_working_days(start_date, 0) == start_date
        assert add_working_days(start_date, -5) == start_date
    
    def test_get_working_days_simple(self):
        """Простой подсчет рабочих дней в диапазоне."""
        start_date = date(2024, 1, 1) # Понедельник
        end_date = date(2024, 1, 7)   # Воскресенье
        # 1, 2, 3, 4, 5 - рабочие. 6, 7 - выходные
        assert get_working_days_count(start_date, end_date) == 5

    def test_get_working_days_with_holidays(self, setup_calendar):
        """Подсчет с учетом кастомного календаря."""
        start_date = date(2024, 1, 8)
        end_date = date(2024, 1, 15)
        # 8 (пн) - вых
        # 9 (вт) - раб
        # 10 (ср) - раб
        # 11 (чт) - раб
        # 12 (пт) - раб
        # 13 (сб) - раб (по календарю)
        # 14 (вс) - вых
        # 15 (пн) - вых (по календарю)
        # Итого: 5 дней
        assert get_working_days_count(start_date, end_date) == 5 