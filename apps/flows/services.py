"""
Сервисный слой для бизнес-логики потоков
"""
from django.db import transaction
from django.utils import timezone
from typing import Optional, List, Dict

from .models import (
    Flow, FlowStep, UserFlow, UserStepProgress, 
    UserQuizAnswer, Task, Quiz
)
from .snapshot_models import (
    TaskSnapshot, QuizSnapshot, ArticleSnapshot,
    QuizQuestionSnapshot, QuizAnswerSnapshot, UserQuizAnswerSnapshot
)


class FlowService:
    """
    Сервис для работы с потоками обучения
    """
    
    @staticmethod
    @transaction.atomic
    def start_flow_for_user(user, flow, expected_completion_date=None, buddy_users=None):
        """
        Запускает поток для пользователя
        
        Args:
            user: Пользователь
            flow: Поток обучения
            expected_completion_date: Ожидаемая дата завершения
            buddy_users: Список бадди для назначения
            
        Returns:
            UserFlow: Созданный объект прохождения
        """
        # Проверяем, нет ли уже активного потока
        if UserFlow.objects.filter(
            user=user, 
            flow=flow, 
            status__in=[UserFlow.FlowStatus.IN_PROGRESS, UserFlow.FlowStatus.PAUSED]
        ).exists():
            raise ValueError("У пользователя уже есть активный поток")
        
        # Создаем UserFlow
        user_flow = UserFlow.objects.create(
            user=user,
            flow=flow,
            expected_completion_date=expected_completion_date,
            status=UserFlow.FlowStatus.IN_PROGRESS
        )
        
        # Назначаем бадди
        if buddy_users:
            from .models import FlowBuddy
            for buddy in buddy_users:
                FlowBuddy.objects.create(
                    user_flow=user_flow,
                    buddy_user=buddy,
                    assigned_by=user  # или текущий пользователь из контекста
                )
        
        return user_flow
    
    @staticmethod
    def complete_article_step(user_flow, step):
        """
        Завершает этап со статьей
        """
        progress, _ = UserStepProgress.objects.get_or_create(
            user_flow=user_flow,
            flow_step=step
        )
        
        if progress.status == UserStepProgress.StepStatus.COMPLETED:
            return progress
        
        progress.article_read_at = timezone.now()
        progress.status = UserStepProgress.StepStatus.COMPLETED
        progress.completed_at = progress.article_read_at
        progress.save()
        
        # Создаем снапшот
        if step.article:
            ArticleSnapshot.objects.create(
                user_step_progress=progress,
                article_title=step.article.title,
                article_content=step.article.content,
                article_summary=step.article.summary or '',
                reading_started_at=progress.article_read_at
            )
        
        # Разблокируем следующий этап
        FlowProgressService.unlock_next_step(user_flow, step)
        
        return progress
    
    @staticmethod
    def complete_task_step(user_flow, step, user_answer):
        """
        Завершает этап с заданием
        """
        task = step.task
        is_correct = task.check_answer(user_answer)
        
        progress, _ = UserStepProgress.objects.get_or_create(
            user_flow=user_flow,
            flow_step=step
        )
        
        # Создаем или обновляем снапшот
        task_snapshot, created = TaskSnapshot.objects.get_or_create(
            user_step_progress=progress,
            defaults={
                'task_title': task.title,
                'task_description': task.description,
                'task_instruction': task.instruction,
                'task_code_word': task.code_word,
                'task_hint': task.hint or '',
                'user_answer': user_answer,
                'is_correct': is_correct,
                'attempts_count': 1
            }
        )
        
        if not created:
            task_snapshot.attempts_count += 1
            task_snapshot.user_answer = user_answer
            task_snapshot.is_correct = is_correct
            task_snapshot.save()
        
        if is_correct:
            progress.task_completed_at = timezone.now()
            progress.status = UserStepProgress.StepStatus.COMPLETED
            progress.completed_at = progress.task_completed_at
            progress.save()
            
            FlowProgressService.unlock_next_step(user_flow, step)
        
        return progress, is_correct


class FlowProgressService:
    """
    Сервис для работы с прогрессом прохождения
    """
    
    @staticmethod
    def unlock_next_step(user_flow, current_step):
        """
        Разблокирует следующий этап после завершения текущего
        """
        next_step = FlowStep.objects.filter(
            flow=user_flow.flow,
            order__gt=current_step.order,
            is_active=True
        ).order_by('order').first()
        
        if next_step:
            next_progress, _ = UserStepProgress.objects.get_or_create(
                user_flow=user_flow,
                flow_step=next_step
            )
            
            if next_progress.status == UserStepProgress.StepStatus.LOCKED:
                next_progress.status = UserStepProgress.StepStatus.AVAILABLE
                next_progress.save()
            
            # Обновляем текущий этап в UserFlow
            user_flow.current_step = next_step
            user_flow.save()
    
    @staticmethod
    def calculate_flow_progress(user_flow) -> Dict:
        """
        Рассчитывает прогресс прохождения потока
        """
        total_steps = user_flow.flow.flow_steps.filter(is_active=True).count()
        completed_steps = user_flow.step_progress.filter(
            status=UserStepProgress.StepStatus.COMPLETED
        ).count()
        
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': round(progress_percentage, 2),
            'is_completed': completed_steps == total_steps
        } 