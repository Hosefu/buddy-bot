"""
Менеджеры для моделей потоков обучения
"""
from django.db import models
from django.utils import timezone


class FlowManager(models.Manager):
    """
    Менеджер для модели Flow
    Предоставляет дополнительные методы для работы с потоками обучения
    """
    
    def active(self):
        """
        Возвращает только активные потоки
        
        Returns:
            QuerySet: Активные потоки обучения
        """
        return self.filter(is_active=True, is_deleted=False)
    
    def mandatory(self):
        """
        Возвращает обязательные потоки
        
        Returns:
            QuerySet: Обязательные потоки обучения
        """
        return self.active().filter(is_mandatory=True)
    
    def for_department(self, department):
        """
        Возвращает потоки для конкретного отдела
        
        Args:
            department (str): Название отдела
            
        Returns:
            QuerySet: Потоки для указанного отдела
        """
        return self.active().filter(
            auto_assign_departments__contains=[department]
        )
    
    def available_for_user(self, user):
        """
        Возвращает потоки, доступные для пользователя
        
        Args:
            user (User): Пользователь
            
        Returns:
            QuerySet: Доступные потоки
        """
        # Получаем обязательные потоки
        available_flows = self.mandatory()
        
        # Добавляем потоки для отдела пользователя
        if user.department:
            department_flows = self.for_department(user.department)
            available_flows = available_flows.union(department_flows)
        
        # Исключаем уже назначенные потоки
        assigned_flow_ids = user.user_flows.values_list('flow_id', flat=True)
        return available_flows.exclude(id__in=assigned_flow_ids)
    
    def with_statistics(self):
        """
        Возвращает потоки с подсчитанной статистикой
        
        Returns:
            QuerySet: Потоки с аннотированной статистикой
        """
        return self.active().annotate(
            total_assignments=models.Count('user_flows'),
            completed_assignments=models.Count(
                'user_flows',
                filter=models.Q(user_flows__status='completed')
            ),
            in_progress_assignments=models.Count(
                'user_flows',
                filter=models.Q(user_flows__status='in_progress')
            ),
            overdue_assignments=models.Count(
                'user_flows',
                filter=models.Q(
                    user_flows__status__in=['not_started', 'in_progress'],
                    user_flows__expected_completion_date__lt=timezone.now().date()
                )
            )
        )


class UserFlowManager(models.Manager):
    """
    Менеджер для модели UserFlow
    Предоставляет методы для работы с прохождением потоков пользователями
    """
    
    def active(self):
        """
        Возвращает только активные прохождения потоков
        
        Returns:
            QuerySet: Активные прохождения
        """
        return self.filter(is_deleted=False)
    
    def for_user(self, user):
        """
        Возвращает прохождения потоков для конкретного пользователя
        
        Args:
            user (User): Пользователь
            
        Returns:
            QuerySet: Прохождения потоков пользователя
        """
        return self.active().filter(user=user)
    
    def in_progress(self):
        """
        Возвращает потоки в процессе выполнения
        
        Returns:
            QuerySet: Потоки в процессе выполнения
        """
        return self.active().filter(status='in_progress')
    
    def completed(self):
        """
        Возвращает завершенные потоки
        
        Returns:
            QuerySet: Завершенные потоки
        """
        return self.active().filter(status='completed')
    
    def overdue(self):
        """
        Возвращает просроченные потоки
        
        Returns:
            QuerySet: Просроченные потоки
        """
        return self.active().filter(
            status__in=['not_started', 'in_progress'],
            expected_completion_date__lt=timezone.now().date()
        )
    
    def paused(self):
        """
        Возвращает приостановленные потоки
        
        Returns:
            QuerySet: Приостановленные потоки
        """
        return self.active().filter(status='paused')
    
    def for_buddy(self, buddy_user):
        """
        Возвращает потоки, где пользователь является бадди
        
        Args:
            buddy_user (User): Бадди
            
        Returns:
            QuerySet: Потоки под опекой бадди
        """
        return self.active().filter(
            flow_buddies__buddy_user=buddy_user,
            flow_buddies__is_active=True
        ).distinct()
    
    def requiring_attention(self):
        """
        Возвращает потоки, требующие внимания (просроченные, долго в процессе)
        
        Returns:
            QuerySet: Потоки, требующие внимания
        """
        from datetime import timedelta
        
        # Дата для определения "долго в процессе" (неделя назад)
        week_ago = timezone.now() - timedelta(days=7)
        
        return self.active().filter(
            models.Q(
                # Просроченные потоки
                status__in=['not_started', 'in_progress'],
                expected_completion_date__lt=timezone.now().date()
            ) | models.Q(
                # Долго в процессе без прогресса
                status='in_progress',
                updated_at__lt=week_ago
            )
        )
    
    def with_progress(self):
        """
        Возвращает потоки с подсчитанным прогрессом
        
        Returns:
            QuerySet: Потоки с аннотированным прогрессом
        """
        return self.active().select_related('user', 'flow').annotate(
            total_steps=models.Count('flow__flow_steps'),
            completed_steps=models.Count(
                'step_progress',
                filter=models.Q(step_progress__status='completed')
            ),
            current_step_order=models.F('current_step__order')
        )
    
    def statistics_by_flow(self):
        """
        Возвращает статистику по потокам
        
        Returns:
            QuerySet: Статистика прохождения по потокам
        """
        return self.active().values('flow__title').annotate(
            total_users=models.Count('id'),
            completed_users=models.Count(
                'id',
                filter=models.Q(status='completed')
            ),
            in_progress_users=models.Count(
                'id',
                filter=models.Q(status='in_progress')
            ),
            overdue_users=models.Count(
                'id',
                filter=models.Q(
                    status__in=['not_started', 'in_progress'],
                    expected_completion_date__lt=timezone.now().date()
                )
            ),
            avg_completion_time=models.Avg(
                models.F('completed_at') - models.F('started_at'),
                filter=models.Q(status='completed')
            )
        ).order_by('flow__title')
    
    def create_with_steps(self, user, flow, **kwargs):
        """
        Создает UserFlow и автоматически создает UserStepProgress для всех этапов
        
        Args:
            user (User): Пользователь
            flow (Flow): Поток обучения
            **kwargs: Дополнительные параметры для UserFlow
            
        Returns:
            UserFlow: Созданный экземпляр прохождения потока
        """
        # Создаем UserFlow
        user_flow = self.create(
            user=user,
            flow=flow,
            **kwargs
        )
        
        # Создаем UserStepProgress для всех этапов потока
        from .models import UserStepProgress
        
        step_progress_list = []
        for step in flow.flow_steps.filter(is_active=True).order_by('order'):
            # Первый этап доступен сразу, остальные заблокированы
            status = 'not_started' if step.order == 1 else 'locked'
            
            step_progress_list.append(
                UserStepProgress(
                    user_flow=user_flow,
                    flow_step=step,
                    status=status
                )
            )
        
        # Массовое создание прогресса по этапам
        UserStepProgress.objects.bulk_create(step_progress_list)
        
        return user_flow


class FlowStepManager(models.Manager):
    """
    Менеджер для модели FlowStep
    Предоставляет методы для работы с этапами потоков
    """
    
    def active(self):
        """
        Возвращает только активные этапы
        
        Returns:
            QuerySet: Активные этапы
        """
        return self.filter(is_active=True, is_deleted=False)
    
    def for_flow(self, flow):
        """
        Возвращает этапы для конкретного потока в правильном порядке
        
        Args:
            flow (Flow): Поток обучения
            
        Returns:
            QuerySet: Этапы потока в порядке выполнения
        """
        return self.active().filter(flow=flow).order_by('order')
    
    def required(self):
        """
        Возвращает только обязательные этапы
        
        Returns:
            QuerySet: Обязательные этапы
        """
        return self.active().filter(is_required=True)
    
    def by_type(self, step_type):
        """
        Возвращает этапы определенного типа
        
        Args:
            step_type (str): Тип этапа
            
        Returns:
            QuerySet: Этапы указанного типа
        """
        return self.active().filter(step_type=step_type)
    
    def with_content(self):
        """
        Возвращает этапы с предзагруженным контентом
        
        Returns:
            QuerySet: Этапы с предзагруженными связанными объектами
        """
        return self.active().select_related('article', 'task', 'quiz')
    
    def reorder_steps(self, flow, step_orders):
        """
        Изменяет порядок этапов в потоке
        
        Args:
            flow (Flow): Поток обучения
            step_orders (dict): Словарь {step_id: new_order}
        """
        with models.transaction.atomic():
            for step_id, new_order in step_orders.items():
                self.filter(id=step_id, flow=flow).update(order=new_order)