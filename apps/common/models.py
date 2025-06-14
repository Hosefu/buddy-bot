"""
Общие модели и миксины для использования в приложениях
"""
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Абстрактная модель с полями времени создания и обновления
    Используется во всех основных моделях системы
    """
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
        help_text='Автоматически устанавливается при создании записи'
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True,
        db_index=True,
        help_text='Автоматически обновляется при изменении записи'
    )
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель с мягким удалением
    Вместо физического удаления помечает запись как удаленную
    """
    is_deleted = models.BooleanField(
        'Удалено',
        default=False,
        db_index=True,
        help_text='Помечает запись как удаленную без физического удаления'
    )
    deleted_at = models.DateTimeField(
        'Дата удаления',
        null=True,
        blank=True,
        help_text='Время когда запись была помечена как удаленная'
    )
    
    def soft_delete(self):
        """Мягкое удаление объекта"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self):
        """Восстановление объекта"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self):
        """
        Метод для физического удаления записи
        """
        super().delete()
    
    class Meta:
        abstract = True


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Базовая модель, объединяющая временные метки и мягкое удаление
    Рекомендуется для использования во всех основных моделях
    """
    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """
    Абстрактная модель для упорядоченных записей
    Используется для этапов флоу, вопросов квизов и т.д.
    """
    order = models.PositiveIntegerField(
        'Порядок',
        default=0,
        help_text='Порядок отображения элементов'
    )
    
    class Meta:
        abstract = True
        ordering = ['order']


class ActiveModel(models.Model):
    """
    Абстрактная модель с флагом активности
    Позволяет временно отключать записи без удаления
    """
    is_active = models.BooleanField(
        'Активно',
        default=True,
        help_text='Определяет, активна ли запись в системе'
    )
    
    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    """
    Базовые варианты статусов для различных моделей
    """
    NOT_STARTED = 'not_started', 'Не начато'
    IN_PROGRESS = 'in_progress', 'В процессе'
    COMPLETED = 'completed', 'Завершено'
    PAUSED = 'paused', 'Приостановлено'
    SUSPENDED = 'suspended', 'Заблокировано'
    SKIPPED = 'skipped', 'Пропущено'
    LOCKED = 'locked', 'Заблокировано'


class WorkingCalendar(models.Model):
    """
    Календарь рабочих дней
    """
    date = models.DateField(
        'Дата',
        unique=True,
        help_text='Дата календаря'
    )
    is_working_day = models.BooleanField(
        'Рабочий день',
        default=True,
        help_text='Является ли день рабочим'
    )
    description = models.CharField(
        'Описание',
        max_length=255,
        blank=True,
        help_text='Описание (например, название праздника)'
    )
    
    class Meta:
        db_table = 'working_calendar'
        verbose_name = 'Календарь рабочих дней'
        verbose_name_plural = 'Календарь рабочих дней'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.date} - {'Рабочий' if self.is_working_day else 'Выходной'}"