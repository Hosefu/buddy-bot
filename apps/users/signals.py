"""
Сигналы для приложения пользователей
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

from .models import User, UserRole, Role
from .tasks import welcome_new_user, update_user_activity


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания нового пользователя
    """
    if created:
        # Назначаем базовую роль "user" всем новым пользователям
        try:
            user_role = Role.objects.filter(name='user').first()
            if not user_role:
                user_role = Role.objects.create(
                    name='user',
                    display_name='Пользователь',
                    description='Базовая роль для всех пользователей'
                )
            
            UserRole.objects.get_or_create(
                user=instance,
                role=user_role,
                defaults={'assigned_by': None}
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка назначения базовой роли пользователю {instance.id}: {str(e)}")
        
        # Отправляем приветственное сообщение (асинхронно)
        if instance.telegram_id:
            welcome_new_user.delay(instance.id)


@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    """
    Обновляет время последнего входа пользователя
    """
    update_user_activity.delay(user.id)


@receiver(post_save, sender=UserRole)
def user_role_assigned_handler(sender, instance, created, **kwargs):
    """
    Обработчик назначения роли пользователю
    """
    if created and instance.is_active:
        # Логируем назначение роли
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Роль '{instance.role.display_name}' назначена пользователю {instance.user.name}"
        )
        
        # Синхронизируем ManyToMany поле roles у пользователя
        # чтобы методы has_role и сериализаторы корректно видели роль
        if not instance.user.roles.filter(id=instance.role.id).exists():
            instance.user.roles.add(instance.role)
            logger.debug(
                f"Роль '{instance.role.name}' добавлена в M2M поле user.roles для {instance.user.name}"
            )
        
        # Если назначена роль buddy, отправляем уведомление
        if instance.role.name == 'buddy':
            from .tasks import send_telegram_notification
            
            message = (
                "🎯 Поздравляем! Вам назначена роль Buddy!\n\n"
                "Теперь вы можете:\n"
                "• Назначать потоки обучения новичкам\n"
                "• Управлять прогрессом подопечных\n"
                "• Помогать в процессе адаптации\n\n"
                "Удачи в наставничестве!"
            )
            
            send_telegram_notification.delay(
                user_id=instance.user.id,
                message=message,
                notification_type='role_assigned'
            )


@receiver(post_delete, sender=User)
def user_deleted_handler(sender, instance, **kwargs):
    """
    Обработчик удаления пользователя
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Пользователь {instance.name} ({instance.email}) был удален")


@receiver(post_save, sender=User)
def user_profile_updated_handler(sender, instance, created, **kwargs):
    """
    Обработчик обновления профиля пользователя
    """
    if not created:
        # Проверяем, изменились ли важные поля
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Логируем важные изменения
            import logging
            logger = logging.getLogger(__name__)
            
            # Проверяем изменение активности
            if hasattr(instance, '_original_is_active'):
                if instance._original_is_active != instance.is_active:
                    status = "активирован" if instance.is_active else "деактивирован"
                    logger.info(f"Пользователь {instance.name} был {status}")
            
            # Проверяем изменение отдела
            if hasattr(instance, '_original_department'):
                if instance._original_department != instance.department:
                    logger.info(
                        f"Пользователь {instance.name} переведен из отдела "
                        f"'{instance._original_department}' в '{instance.department}'"
                    )
                    
                    # Автоматически назначаем потоки для нового отдела
                    if instance.department:
                        from apps.flows.tasks import auto_assign_flows_to_new_user
                        auto_assign_flows_to_new_user.delay(instance.id)


# Для отслеживания изменений значений полей
@receiver(post_save, sender=User)
def store_user_original_values(sender, instance, **kwargs):
    """
    Сохраняет оригинальные значения полей для отслеживания изменений
    """
    if instance.pk:
        try:
            original = User.objects.get(pk=instance.pk)
            instance._original_is_active = original.is_active
            instance._original_department = original.department
        except User.DoesNotExist:
            pass