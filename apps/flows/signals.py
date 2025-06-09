"""
Сигналы для приложения потоков обучения
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    UserFlow, FlowBuddy, UserStepProgress, UserQuizAnswer, 
    FlowStep, FlowAction
)


@receiver(post_save, sender=UserFlow)
def user_flow_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания UserFlow
    """
    if created:
        # Записываем действие о запуске потока
        FlowAction.objects.create(
            user_flow=instance,
            action_type=FlowAction.ActionType.STARTED,
            performed_by=instance.user,
            reason='Поток запущен автоматически'
        )
        
        # Уведомляем бадди о новом назначении
        active_buddies = instance.flow_buddies.filter(is_active=True)
        for flow_buddy in active_buddies:
            from apps.users.tasks import notify_buddy_assignment
            notify_buddy_assignment.delay(
                buddy_user_id=flow_buddy.buddy_user.id,
                mentee_user_id=instance.user.id,
                flow_title=instance.flow.title
            )


@receiver(post_save, sender=UserFlow)
def user_flow_completed_handler(sender, instance, created, **kwargs):
    """
    Обработчик завершения потока
    """
    if not created and instance.status == 'completed' and instance.completed_at:
        # Отправляем уведомления о завершении
        from .tasks import notify_flow_completion
        notify_flow_completion.delay(instance.id)
        
        # Записываем действие о завершении
        FlowAction.objects.get_or_create(
            user_flow=instance,
            action_type=FlowAction.ActionType.COMPLETED,
            performed_by=instance.user,
            defaults={
                'reason': 'Поток успешно завершен',
                'metadata': {
                    'completion_time': str(instance.completed_at - instance.started_at) if instance.started_at else None,
                    'progress_percentage': instance.progress_percentage
                }
            }
        )


@receiver(post_save, sender=UserStepProgress)
def step_progress_updated_handler(sender, instance, created, **kwargs):
    """
    Обработчик обновления прогресса по этапу
    """
    if instance.status == 'completed' and instance.completed_at:
        # Уведомляем о завершении этапа
        from .tasks import notify_step_completion
        notify_step_completion.delay(instance.user_flow.id, instance.flow_step.id)
        
        # Проверяем, завершен ли весь поток
        total_required_steps = instance.user_flow.flow.flow_steps.filter(
            is_required=True, 
            is_active=True
        ).count()
        
        completed_required_steps = instance.user_flow.step_progress.filter(
            flow_step__is_required=True,
            flow_step__is_active=True,
            status='completed'
        ).count()
        
        # Если все обязательные этапы завершены, завершаем поток
        if completed_required_steps >= total_required_steps:
            instance.user_flow.complete()
        
        # Разблокируем следующий этап
        next_step = FlowStep.objects.filter(
            flow=instance.flow_step.flow,
            order=instance.flow_step.order + 1,
            is_active=True
        ).first()
        
        if next_step:
            next_progress, created = UserStepProgress.objects.get_or_create(
                user_flow=instance.user_flow,
                flow_step=next_step,
                defaults={'status': 'not_started'}
            )
            
            if next_progress.status == 'locked':
                next_progress.status = 'not_started'
                next_progress.save()


@receiver(post_save, sender=UserQuizAnswer)
def quiz_answer_submitted_handler(sender, instance, created, **kwargs):
    """
    Обработчик отправки ответа на квиз
    """
    if created:
        # Проверяем, завершен ли квиз
        quiz = instance.question.quiz
        total_questions = quiz.total_questions
        user_answers = UserQuizAnswer.objects.filter(
            user_flow=instance.user_flow,
            question__quiz=quiz
        ).count()
        
        if user_answers >= total_questions:
            # Подсчитываем правильные ответы
            correct_answers = UserQuizAnswer.objects.filter(
                user_flow=instance.user_flow,
                question__quiz=quiz,
                is_correct=True
            ).count()
            
            # Обновляем прогресс по этапу
            try:
                step_progress = UserStepProgress.objects.get(
                    user_flow=instance.user_flow,
                    flow_step=quiz.flow_step
                )
                
                step_progress.quiz_completed_at = timezone.now()
                step_progress.quiz_correct_answers = correct_answers
                step_progress.quiz_total_questions = total_questions
                
                # Проверяем прохождение
                if quiz.is_passing_score(correct_answers):
                    step_progress.status = 'completed'
                    step_progress.completed_at = timezone.now()
                
                step_progress.save()
                
            except UserStepProgress.DoesNotExist:
                pass


@receiver(post_save, sender=FlowBuddy)
def flow_buddy_assigned_handler(sender, instance, created, **kwargs):
    """
    Обработчик назначения бадди
    """
    if created and instance.is_active:
        # Записываем действие о назначении бадди
        FlowAction.objects.create(
            user_flow=instance.user_flow,
            action_type='buddy_assigned',
            performed_by=instance.assigned_by,
            reason=f'Назначен бадди: {instance.buddy_user.name}',
            metadata={
                'buddy_user_id': instance.buddy_user.id,
                'buddy_name': instance.buddy_user.name
            }
        )


@receiver(pre_save, sender=UserFlow)
def user_flow_status_changed_handler(sender, instance, **kwargs):
    """
    Обработчик изменения статуса потока
    """
    if instance.pk:
        try:
            old_instance = UserFlow.objects.get(pk=instance.pk)
            
            # Если статус изменился на completed
            if (old_instance.status != 'completed' and 
                instance.status == 'completed' and 
                not instance.completed_at):
                instance.completed_at = timezone.now()
            
            # Если статус изменился на in_progress
            if (old_instance.status == 'not_started' and 
                instance.status == 'in_progress' and 
                not instance.started_at):
                instance.started_at = timezone.now()
                
        except UserFlow.DoesNotExist:
            pass


@receiver(post_delete, sender=UserFlow)
def user_flow_deleted_handler(sender, instance, **kwargs):
    """
    Обработчик удаления потока
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        f"Поток '{instance.flow.title}' удален для пользователя {instance.user.name}"
    )


@receiver(post_save, sender=FlowStep)
def flow_step_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания нового этапа потока
    """
    if created:
        # Создаем UserStepProgress для всех существующих UserFlow этого потока
        user_flows = UserFlow.objects.filter(flow=instance.flow)
        
        for user_flow in user_flows:
            # Определяем статус нового этапа
            if instance.order == 1:
                status = 'not_started'
            else:
                # Проверяем, завершен ли предыдущий этап
                prev_step = FlowStep.objects.filter(
                    flow=instance.flow,
                    order=instance.order - 1
                ).first()
                
                if prev_step:
                    prev_progress = UserStepProgress.objects.filter(
                        user_flow=user_flow,
                        flow_step=prev_step,
                        status='completed'
                    ).exists()
                    status = 'not_started' if prev_progress else 'locked'
                else:
                    status = 'not_started'
            
            UserStepProgress.objects.get_or_create(
                user_flow=user_flow,
                flow_step=instance,
                defaults={'status': status}
            )