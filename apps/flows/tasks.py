"""
Celery задачи для системы потоков обучения
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, datetime
import logging

logger = logging.getLogger('apps.flows.tasks')


@shared_task(bind=True, max_retries=3)
def check_overdue_flows(self):
    """
    Проверяет просроченные потоки и отправляет уведомления
    """
    try:
        from .models import UserFlow, FlowAction
        from apps.users.tasks import send_telegram_notification
        
        # Находим просроченные потоки
        overdue_flows = UserFlow.objects.overdue().select_related(
            'user', 'flow'
        ).prefetch_related('flow_buddies__buddy_user')
        
        notifications_sent = 0
        
        for user_flow in overdue_flows:
            try:
                # Проверяем, не отправляли ли уведомление недавно
                recent_notification = FlowAction.objects.filter(
                    user_flow=user_flow,
                    action_type='notification_sent',
                    performed_at__gte=timezone.now() - timedelta(days=1)
                ).exists()
                
                if not recent_notification:
                    # Отправляем уведомление пользователю
                    message = (
                        f"⚠️ Поток обучения '{user_flow.flow.title}' просрочен!\n"
                        f"Дедлайн был: {user_flow.expected_completion_date}\n"
                        f"Пожалуйста, обратитесь к своему бадди."
                    )
                    
                    send_telegram_notification.delay(
                        user_id=user_flow.user.id,
                        message=message,
                        notification_type='overdue_flow'
                    )
                    
                    # Отправляем уведомления бадди
                    for flow_buddy in user_flow.flow_buddies.filter(is_active=True):
                        buddy_message = (
                            f"⚠️ У подопечного {user_flow.user.name} просрочен поток "
                            f"'{user_flow.flow.title}'\n"
                            f"Прогресс: {user_flow.progress_percentage:.1f}%\n"
                            f"Дедлайн был: {user_flow.expected_completion_date}"
                        )
                        
                        send_telegram_notification.delay(
                            user_id=flow_buddy.buddy_user.id,
                            message=buddy_message,
                            notification_type='buddy_overdue_alert'
                        )
                    
                    # Записываем действие
                    FlowAction.objects.create(
                        user_flow=user_flow,
                        action_type='notification_sent',
                        performed_by=None,
                        reason='Автоматическое уведомление о просрочке',
                        metadata={
                            'notification_type': 'overdue_flow',
                            'overdue_days': (timezone.now().date() - user_flow.expected_completion_date).days
                        }
                    )
                    
                    notifications_sent += 1
                    
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления для потока {user_flow.id}: {str(e)}")
                continue
        
        logger.info(f"Проверка просроченных потоков завершена. Отправлено уведомлений: {notifications_sent}")
        return {
            'overdue_flows_count': overdue_flows.count(),
            'notifications_sent': notifications_sent
        }
        
    except Exception as exc:
        logger.error(f"Ошибка в задаче check_overdue_flows: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_flow_reminders(self):
    """
    Отправляет напоминания о незавершенных потоках
    """
    try:
        from .models import UserFlow
        from apps.users.tasks import send_telegram_notification
        
        # Находим потоки в работе без активности более 3 дней
        stale_flows = UserFlow.objects.filter(
            status='in_progress',
            updated_at__lt=timezone.now() - timedelta(days=3)
        ).select_related('user', 'flow', 'current_step')
        
        reminders_sent = 0
        
        for user_flow in stale_flows:
            try:
                current_step_info = ""
                if user_flow.current_step:
                    current_step_info = f"\nТекущий этап: {user_flow.current_step.title}"
                
                message = (
                    f"📚 Напоминание о потоке обучения '{user_flow.flow.title}'\n"
                    f"Прогресс: {user_flow.progress_percentage:.1f}%"
                    f"{current_step_info}\n"
                    f"Продолжите обучение, чтобы не отстать от графика!"
                )
                
                send_telegram_notification.delay(
                    user_id=user_flow.user.id,
                    message=message,
                    notification_type='flow_reminder'
                )
                
                reminders_sent += 1
                
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания для потока {user_flow.id}: {str(e)}")
                continue
        
        logger.info(f"Отправлено напоминаний: {reminders_sent}")
        return {
            'stale_flows_count': stale_flows.count(),
            'reminders_sent': reminders_sent
        }
        
    except Exception as exc:
        logger.error(f"Ошибка в задаче send_flow_reminders: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def generate_daily_statistics(self):
    """
    Генерирует ежедневную статистику системы
    """
    try:
        from .models import UserFlow, Flow
        from apps.users.models import User
        
        today = timezone.now().date()
        
        # Общая статистика
        total_users = User.objects.active_users().count()
        total_flows = Flow.objects.active().count()
        
        # Статистика потоков
        active_flows = UserFlow.objects.filter(status='in_progress').count()
        completed_today = UserFlow.objects.filter(
            completed_at__date=today
        ).count()
        overdue_flows = UserFlow.objects.overdue().count()
        
        # Статистика завершаемости
        total_assignments = UserFlow.objects.active().count()
        completed_assignments = UserFlow.objects.completed().count()
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # Сохраняем статистику в Redis или базу данных
        statistics = {
            'date': str(today),
            'users': {
                'total': total_users,
                'with_active_flows': active_flows
            },
            'flows': {
                'total': total_flows,
                'active_assignments': active_flows,
                'completed_today': completed_today,
                'overdue': overdue_flows,
                'completion_rate': round(completion_rate, 2)
            }
        }
        
        # Здесь можно сохранить статистику в Redis
        # from django.core.cache import cache
        # cache.set(f'daily_stats_{today}', statistics, timeout=60*60*24*7)  # неделя
        
        logger.info(f"Статистика за {today} сгенерирована: {statistics}")
        return statistics
        
    except Exception as exc:
        logger.error(f"Ошибка генерации статистики: {str(exc)}")
        raise


@shared_task(bind=True, max_retries=3)
def notify_flow_completion(self, user_flow_id):
    """
    Отправляет уведомление о завершении потока
    """
    try:
        from .models import UserFlow
        from apps.users.tasks import send_telegram_notification
        
        user_flow = UserFlow.objects.select_related('user', 'flow').get(id=user_flow_id)
        
        # Уведомление пользователю
        message = (
            f"🎉 Поздравляем! Вы успешно завершили поток обучения "
            f"'{user_flow.flow.title}'!\n"
            f"Время прохождения: {user_flow.completed_at - user_flow.started_at}\n"
            f"Отличная работа!"
        )
        
        send_telegram_notification.delay(
            user_id=user_flow.user.id,
            message=message,
            notification_type='flow_completed'
        )
        
        # Уведомления бадди
        for flow_buddy in user_flow.flow_buddies.filter(is_active=True):
            buddy_message = (
                f"✅ Подопечный {user_flow.user.name} завершил поток "
                f"'{user_flow.flow.title}'\n"
                f"Время прохождения: {user_flow.completed_at - user_flow.started_at}"
            )
            
            send_telegram_notification.delay(
                user_id=flow_buddy.buddy_user.id,
                message=buddy_message,
                notification_type='buddy_completion_alert'
            )
        
        logger.info(f"Уведомления о завершении потока {user_flow_id} отправлены")
        return True
        
    except UserFlow.DoesNotExist:
        logger.error(f"UserFlow {user_flow_id} не найден")
        return False
    except Exception as exc:
        logger.error(f"Ошибка отправки уведомления о завершении: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def notify_step_completion(self, user_flow_id, step_id):
    """
    Отправляет уведомление о завершении этапа
    """
    try:
        from .models import UserFlow, FlowStep
        from apps.users.tasks import send_telegram_notification
        
        user_flow = UserFlow.objects.select_related('user', 'flow').get(id=user_flow_id)
        step = FlowStep.objects.get(id=step_id)
        
        # Проверяем, важный ли это этап (например, последний или ключевой)
        total_steps = user_flow.flow.total_steps
        completed_steps = user_flow.step_progress.filter(status='completed').count()
        
        # Отправляем уведомление только для важных этапов
        if step.order % 3 == 0 or completed_steps == total_steps // 2:  # каждый 3-й этап или середина
            message = (
                f"📋 Этап '{step.title}' завершен!\n"
                f"Поток: {user_flow.flow.title}\n"
                f"Прогресс: {user_flow.progress_percentage:.1f}%\n"
                f"Продолжайте в том же духе!"
            )
            
            send_telegram_notification.delay(
                user_id=user_flow.user.id,
                message=message,
                notification_type='step_completed'
            )
        
        return True
        
    except (UserFlow.DoesNotExist, FlowStep.DoesNotExist):
        logger.error(f"UserFlow {user_flow_id} или Step {step_id} не найден")
        return False
    except Exception as exc:
        logger.error(f"Ошибка отправки уведомления о завершении этапа: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def auto_assign_flows_to_new_user(self, user_id):
    """
    Автоматически назначает обязательные потоки новому пользователю
    """
    try:
        from apps.users.models import User
        from .models import Flow, UserFlow
        
        user = User.objects.get(id=user_id)
        
        # Находим обязательные потоки
        mandatory_flows = Flow.objects.mandatory()
        
        # Находим потоки для отдела пользователя
        department_flows = Flow.objects.filter(
            auto_assign_departments__contains=[user.department]
        ) if user.department else Flow.objects.none()
        
        # Объединяем потоки
        flows_to_assign = mandatory_flows.union(department_flows)
        
        assigned_count = 0
        for flow in flows_to_assign:
            # Проверяем, не назначен ли уже поток
            if not UserFlow.objects.filter(user=user, flow=flow).exists():
                UserFlow.objects.create_with_steps(
                    user=user,
                    flow=flow,
                    expected_completion_date=timezone.now().date() + timedelta(days=30)
                )
                assigned_count += 1
        
        logger.info(f"Пользователю {user.name} автоматически назначено потоков: {assigned_count}")
        return {
            'user_id': user_id,
            'assigned_flows': assigned_count
        }
        
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден")
        return False
    except Exception as exc:
        logger.error(f"Ошибка автоназначения потоков: {str(exc)}")
        raise


@shared_task(bind=True)
def cleanup_old_flow_data(self):
    """
    Очищает старые данные потоков
    """
    try:
        from .models import FlowAction, UserQuizAnswer
        
        # Удаляем старые действия (старше года)
        old_actions = FlowAction.objects.filter(
            performed_at__lt=timezone.now() - timedelta(days=365)
        )
        deleted_actions = old_actions.count()
        old_actions.delete()
        
        # Удаляем старые ответы на квизы завершенных потоков (старше 6 месяцев)
        old_answers = UserQuizAnswer.objects.filter(
            answered_at__lt=timezone.now() - timedelta(days=180),
            user_flow__status='completed'
        )
        deleted_answers = old_answers.count()
        old_answers.delete()
        
        logger.info(f"Очистка данных: удалено {deleted_actions} действий, {deleted_answers} ответов")
        return {
            'deleted_actions': deleted_actions,
            'deleted_answers': deleted_answers
        }
        
    except Exception as exc:
        logger.error(f"Ошибка очистки данных: {str(exc)}")
        raise