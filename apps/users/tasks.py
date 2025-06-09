"""
Celery задачи для пользователей и Telegram интеграции
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging
import requests

logger = logging.getLogger('apps.users.tasks')


@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, user_id, message, notification_type='general', **kwargs):
    """
    Отправляет уведомление пользователю в Telegram
    
    Args:
        user_id (int): ID пользователя в системе
        message (str): Текст сообщения
        notification_type (str): Тип уведомления
        **kwargs: Дополнительные параметры (кнопки, форматирование и т.д.)
    """
    try:
        from .models import User
        
        # Получаем пользователя
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            logger.error(f"Пользователь {user_id} не найден")
            return False
        
        # Проверяем наличие Telegram ID
        if not user.telegram_id:
            logger.warning(f"У пользователя {user.name} нет Telegram ID")
            return False
        
        # Проверяем настройки бота
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не настроен")
            return False
        
        # Формируем URL для API Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Базовые параметры
        data = {
            'chat_id': user.telegram_id,
            'text': message,
            'parse_mode': kwargs.get('parse_mode', 'HTML'),
            'disable_web_page_preview': kwargs.get('disable_preview', True)
        }
        
        # Добавляем кнопки если есть
        if 'keyboard' in kwargs:
            data['reply_markup'] = kwargs['keyboard']
        
        # Отправляем запрос
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Уведомление типа '{notification_type}' отправлено пользователю {user.name}")
            
            # Записываем статистику отправки
            _record_notification_stats(user_id, notification_type, True)
            return True
        else:
            logger.error(f"Ошибка отправки уведомления: {response.status_code} - {response.text}")
            _record_notification_stats(user_id, notification_type, False, response.text)
            return False
            
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при отправке уведомления: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    except Exception as exc:
        logger.error(f"Ошибка отправки Telegram уведомления: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_bulk_telegram_notifications(self, user_ids, message, notification_type='bulk'):
    """
    Массовая отправка уведомлений группе пользователей
    
    Args:
        user_ids (list): Список ID пользователей
        message (str): Текст сообщения
        notification_type (str): Тип уведомления
    """
    try:
        from .models import User
        
        users = User.objects.filter(
            id__in=user_ids,
            is_active=True,
            telegram_id__isnull=False
        ).exclude(telegram_id='')
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                result = send_telegram_notification.delay(
                    user_id=user.id,
                    message=message,
                    notification_type=notification_type
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления пользователю {user.id}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Массовая рассылка завершена: отправлено {sent_count}, ошибок {failed_count}")
        return {
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_users': len(user_ids)
        }
        
    except Exception as exc:
        logger.error(f"Ошибка массовой рассылки: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def cleanup_expired_sessions(self):
    """
    Очищает истекшие Telegram сессии
    """
    try:
        from .models import TelegramSession
        
        # Удаляем истекшие сессии
        expired_sessions = TelegramSession.objects.filter(
            expires_at__lt=timezone.now()
        )
        deleted_count = expired_sessions.count()
        expired_sessions.delete()
        
        # Помечаем как невалидные сессии старше недели
        old_sessions = TelegramSession.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=7),
            is_valid=True
        )
        updated_count = old_sessions.update(is_valid=False)
        
        logger.info(f"Очистка сессий: удалено {deleted_count}, деактивировано {updated_count}")
        return {
            'deleted_sessions': deleted_count,
            'deactivated_sessions': updated_count
        }
        
    except Exception as exc:
        logger.error(f"Ошибка очистки сессий: {str(exc)}")
        raise


@shared_task(bind=True, max_retries=3)
def sync_user_with_telegram(self, user_id, telegram_data):
    """
    Синхронизирует данные пользователя с Telegram
    
    Args:
        user_id (int): ID пользователя
        telegram_data (dict): Данные от Telegram API
    """
    try:
        from .models import User
        
        user = User.objects.get(id=user_id)
        
        # Обновляем данные пользователя
        updated_fields = []
        
        if 'first_name' in telegram_data:
            new_name = telegram_data['first_name']
            if 'last_name' in telegram_data:
                new_name += f" {telegram_data['last_name']}"
            
            if user.name != new_name:
                user.name = new_name
                updated_fields.append('name')
        
        if 'username' in telegram_data and user.telegram_username != telegram_data['username']:
            user.telegram_username = telegram_data['username']
            updated_fields.append('telegram_username')
        
        if updated_fields:
            user.save(update_fields=updated_fields + ['updated_at'])
            logger.info(f"Синхронизированы поля пользователя {user.id}: {updated_fields}")
        
        return {
            'user_id': user_id,
            'updated_fields': updated_fields
        }
        
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден для синхронизации")
        return False
    except Exception as exc:
        logger.error(f"Ошибка синхронизации пользователя: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def generate_user_statistics(self):
    """
    Генерирует статистику пользователей
    """
    try:
        from .models import User, UserRole
        from django.db.models import Count
        
        # Общая статистика пользователей
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        telegram_users = User.objects.filter(telegram_id__isnull=False).exclude(telegram_id='').count()
        
        # Статистика по ролям
        role_stats = UserRole.objects.filter(is_active=True).values(
            'role__name', 'role__display_name'
        ).annotate(count=Count('user')).order_by('-count')
        
        # Статистика по отделам
        department_stats = User.objects.filter(
            is_active=True,
            department__isnull=False
        ).exclude(department='').values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Статистика регистраций за последнюю неделю
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = User.objects.filter(created_at__gte=week_ago).count()
        
        statistics = {
            'date': str(timezone.now().date()),
            'users': {
                'total': total_users,
                'active': active_users,
                'with_telegram': telegram_users,
                'new_this_week': new_users_week
            },
            'roles': list(role_stats),
            'departments': list(department_stats)
        }
        
        logger.info(f"Статистика пользователей сгенерирована: {statistics}")
        return statistics
        
    except Exception as exc:
        logger.error(f"Ошибка генерации статистики пользователей: {str(exc)}")
        raise


@shared_task(bind=True, max_retries=3)
def welcome_new_user(self, user_id):
    """
    Отправляет приветственное сообщение новому пользователю
    
    Args:
        user_id (int): ID нового пользователя
    """
    try:
        from .models import User
        
        user = User.objects.get(id=user_id)
        
        if not user.telegram_id:
            logger.info(f"Пользователь {user.name} не имеет Telegram ID, приветствие не отправлено")
            return False
        
        welcome_message = (
            f"👋 Добро пожаловать в систему онбординга, {user.name}!\n\n"
            f"🎯 Здесь вы сможете:\n"
            f"• Проходить обучающие потоки\n"
            f"• Изучать статьи и гайды\n"
            f"• Отслеживать свой прогресс\n"
            f"• Получать помощь от бадди\n\n"
            f"📱 Для удобства используйте Telegram Mini App\n"
            f"📚 Удачи в обучении!"
        )
        
        # Отправляем приветственное сообщение
        send_telegram_notification.delay(
            user_id=user_id,
            message=welcome_message,
            notification_type='welcome'
        )
        
        # Автоматически назначаем обязательные потоки
        from apps.flows.tasks import auto_assign_flows_to_new_user
        auto_assign_flows_to_new_user.delay(user_id)
        
        logger.info(f"Приветственное сообщение отправлено пользователю {user.name}")
        return True
        
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден")
        return False
    except Exception as exc:
        logger.error(f"Ошибка отправки приветствия: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def update_user_activity(self, user_id):
    """
    Обновляет время последней активности пользователя
    
    Args:
        user_id (int): ID пользователя
    """
    try:
        from .models import User
        
        User.objects.filter(id=user_id).update(
            last_login_at=timezone.now()
        )
        
        return True
        
    except Exception as exc:
        logger.error(f"Ошибка обновления активности пользователя {user_id}: {str(exc)}")
        return False


@shared_task(bind=True, max_retries=3)
def notify_buddy_assignment(self, buddy_user_id, mentee_user_id, flow_title):
    """
    Уведомляет бадди о назначении нового подопечного
    
    Args:
        buddy_user_id (int): ID бадди
        mentee_user_id (int): ID подопечного
        flow_title (str): Название потока
    """
    try:
        from .models import User
        
        buddy = User.objects.get(id=buddy_user_id)
        mentee = User.objects.get(id=mentee_user_id)
        
        message = (
            f"👥 Вам назначен новый подопечный!\n\n"
            f"Пользователь: {mentee.name}\n"
            f"Поток обучения: {flow_title}\n"
            f"Отдел: {mentee.department or 'Не указан'}\n"
            f"Должность: {mentee.position or 'Не указана'}\n\n"
            f"💡 Рекомендуется связаться с подопечным и предложить помощь в начале обучения."
        )
        
        send_telegram_notification.delay(
            user_id=buddy_user_id,
            message=message,
            notification_type='buddy_assignment'
        )
        
        logger.info(f"Уведомление о назначении отправлено бадди {buddy.name}")
        return True
        
    except User.DoesNotExist:
        logger.error(f"Пользователь не найден: buddy_id={buddy_user_id}, mentee_id={mentee_user_id}")
        return False
    except Exception as exc:
        logger.error(f"Ошибка уведомления о назначении бадди: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


def _record_notification_stats(user_id, notification_type, success, error_message=None):
    """
    Записывает статистику отправки уведомлений
    
    Args:
        user_id (int): ID пользователя
        notification_type (str): Тип уведомления
        success (bool): Успешность отправки
        error_message (str): Сообщение об ошибке
    """
    try:
        # Здесь можно записать статистику в Redis или отдельную таблицу
        # Пока просто логируем
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"Notification stats: user={user_id}, type={notification_type}, "
            f"status={status}, error={error_message}"
        )
    except Exception as e:
        logger.error(f"Ошибка записи статистики уведомлений: {str(e)}")


@shared_task(bind=True)
def send_daily_digest(self, user_id):
    """
    Отправляет ежедневную сводку пользователю
    
    Args:
        user_id (int): ID пользователя
    """
    try:
        from .models import User
        from apps.flows.models import UserFlow
        
        user = User.objects.get(id=user_id, is_active=True)
        
        if not user.telegram_id:
            return False
        
        # Собираем информацию о потоках пользователя
        active_flows = UserFlow.objects.filter(
            user=user,
            status='in_progress'
        ).select_related('flow', 'current_step')
        
        if not active_flows.exists():
            return False  # Нет активных потоков
        
        # Формируем сообщение
        message_parts = [f"📊 Ваша сводка на {timezone.now().strftime('%d.%m.%Y')}:"]
        
        for user_flow in active_flows:
            progress = user_flow.progress_percentage
            current_step = user_flow.current_step.title if user_flow.current_step else "Завершено"
            
            status_emoji = "🟢" if progress > 70 else "🟡" if progress > 30 else "🔴"
            
            message_parts.append(
                f"\n{status_emoji} {user_flow.flow.title}\n"
                f"   Прогресс: {progress:.1f}%\n"
                f"   Текущий этап: {current_step}"
            )
            
            # Добавляем информацию о дедлайне если есть
            if user_flow.expected_completion_date:
                days_left = (user_flow.expected_completion_date - timezone.now().date()).days
                if days_left <= 7:
                    message_parts.append(f"   ⏰ Осталось дней: {days_left}")
        
        message_parts.append("\n💪 Продолжайте обучение!")
        
        message = '\n'.join(message_parts)
        
        send_telegram_notification.delay(
            user_id=user_id,
            message=message,
            notification_type='daily_digest'
        )
        
        return True
        
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден для дайджеста")
        return False
    except Exception as exc:
        logger.error(f"Ошибка отправки дайджеста: {str(exc)}")
        raise