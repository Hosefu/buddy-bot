"""
Общие миксины для views и других компонентов
"""
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import PermissionDenied


class TimestampMixin:
    """
    Миксин для автоматического обновления временных меток
    """
    def perform_create(self, serializer):
        """Устанавливает временные метки при создании"""
        serializer.save(
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
    
    def perform_update(self, serializer):
        """Обновляет временную метку при изменении"""
        serializer.save(updated_at=timezone.now())


class SoftDeleteMixin:
    """
    Миксин для мягкого удаления объектов
    """
    def perform_destroy(self, instance):
        """Мягкое удаление вместо физического"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])
    
    def get_queryset(self):
        """Исключает удаленные объекты из запросов"""
        queryset = super().get_queryset()
        if hasattr(queryset.model, 'is_deleted'):
            return queryset.filter(is_deleted=False)
        return queryset


class ActiveObjectsMixin:
    """
    Миксин для фильтрации только активных объектов
    """
    def get_queryset(self):
        """Возвращает только активные объекты"""
        queryset = super().get_queryset()
        if hasattr(queryset.model, 'is_active'):
            return queryset.filter(is_active=True)
        return queryset


class UserFilterMixin:
    """
    Миксин для фильтрации объектов по текущему пользователю
    """
    user_field = 'user'  # Поле для фильтрации по пользователю
    
    def get_queryset(self):
        """Фильтрует объекты по текущему пользователю"""
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            filter_kwargs = {self.user_field: self.request.user}
            return queryset.filter(**filter_kwargs)
        return queryset.none()


class SearchMixin:
    """
    Миксин для поиска по нескольким полям
    """
    search_fields = []
    
    def get_queryset(self):
        """Добавляет поиск к базовому queryset"""
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', '').strip()
        
        if search_query and self.search_fields:
            search_q = Q()
            for field in self.search_fields:
                search_q |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(search_q)
        
        return queryset


class OrderingMixin:
    """
    Миксин для сортировки результатов
    """
    default_ordering = ['-created_at']
    allowed_ordering_fields = []
    
    def get_queryset(self):
        """Добавляет сортировку к queryset"""
        queryset = super().get_queryset()
        ordering = self.get_ordering()
        
        if ordering:
            return queryset.order_by(*ordering)
        return queryset
    
    def get_ordering(self):
        """Получает параметры сортировки"""
        ordering_param = self.request.query_params.get('ordering', '').strip()
        
        if ordering_param:
            # Разбираем параметр сортировки
            ordering_fields = []
            for field in ordering_param.split(','):
                field = field.strip()
                if field.startswith('-'):
                    field_name = field[1:]
                    if field_name in self.allowed_ordering_fields:
                        ordering_fields.append(field)
                else:
                    if field in self.allowed_ordering_fields:
                        ordering_fields.append(field)
            
            if ordering_fields:
                return ordering_fields
        
        return self.default_ordering


class PaginationMixin:
    """
    Миксин для кастомной пагинации
    """
    def get_paginated_response(self, data):
        """Кастомный формат ответа пагинации"""
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class RoleBasedPermissionMixin:
    """
    Миксин для проверки разрешений на основе ролей
    """
    required_roles = []
    role_permissions = {}  # {'role_name': ['permission1', 'permission2']}
    
    def check_permissions(self, request):
        """Проверяет разрешения на основе ролей"""
        super().check_permissions(request)
        
        if not request.user.is_authenticated:
            return
        
        # Проверяем обязательные роли
        if self.required_roles:
            user_has_required_role = any(
                request.user.has_role(role) for role in self.required_roles
            )
            if not user_has_required_role:
                raise PermissionDenied("Недостаточно прав для выполнения действия")
        
        # Проверяем права для конкретной роли
        if self.role_permissions:
            action = self.action if hasattr(self, 'action') else request.method.lower()
            
            for role, permissions in self.role_permissions.items():
                if request.user.has_role(role) and action in permissions:
                    return
            
            # Если дошли сюда и есть role_permissions, значит нет прав
            if self.role_permissions:
                raise PermissionDenied("Действие не разрешено для вашей роли")


class OwnershipMixin:
    """
    Миксин для проверки владения объектом
    """
    ownership_field = 'user'
    
    def check_object_permissions(self, request, obj):
        """Проверяет права на объект"""
        super().check_object_permissions(request, obj)
        
        # Модераторы имеют доступ ко всем объектам
        if request.user.has_role('moderator'):
            return
        
        # Проверяем владение объектом
        owner = getattr(obj, self.ownership_field, None)
        if owner and owner != request.user:
            raise PermissionDenied("У вас нет прав на этот объект")


class AuditMixin:
    """
    Миксин для логирования действий пользователей
    """
    def perform_create(self, serializer):
        """Логирует создание объекта"""
        instance = serializer.save()
        self.log_action('create', instance)
        return instance
    
    def perform_update(self, serializer):
        """Логирует обновление объекта"""
        instance = serializer.save()
        self.log_action('update', instance)
        return instance
    
    def perform_destroy(self, instance):
        """Логирует удаление объекта"""
        self.log_action('delete', instance)
        super().perform_destroy(instance)
    
    def log_action(self, action, instance):
        """Логирует действие пользователя"""
        import logging
        logger = logging.getLogger('user_actions')
        
        logger.info(f"User {self.request.user.id} performed {action} on {instance.__class__.__name__} {instance.id}")


class CacheMixin:
    """
    Миксин для кеширования ответов
    """
    cache_timeout = 300  # 5 минут по умолчанию
    cache_key_prefix = 'api'
    
    def get_cache_key(self):
        """Генерирует ключ кеша"""
        path = self.request.path
        query_params = self.request.query_params.urlencode()
        user_id = self.request.user.id if self.request.user.is_authenticated else 'anonymous'
        
        return f"{self.cache_key_prefix}:{user_id}:{path}:{query_params}"
    
    def get_cached_response(self):
        """Получает ответ из кеша"""
        from django.core.cache import cache
        
        cache_key = self.get_cache_key()
        return cache.get(cache_key)
    
    def set_cached_response(self, response_data):
        """Сохраняет ответ в кеш"""
        from django.core.cache import cache
        
        cache_key = self.get_cache_key()
        cache.set(cache_key, response_data, self.cache_timeout)


class ErrorHandlingMixin:
    """
    Миксин для обработки ошибок
    """
    def handle_exception(self, exc):
        """Кастомная обработка исключений"""
        import logging
        logger = logging.getLogger('api_errors')
        
        # Логируем ошибку
        logger.error(f"API Error: {exc}", extra={
            'user_id': self.request.user.id if self.request.user.is_authenticated else None,
            'path': self.request.path,
            'method': self.request.method,
            'data': self.request.data if hasattr(self.request, 'data') else None
        })
        
        return super().handle_exception(exc)


class ValidationMixin:
    """
    Миксин для дополнительной валидации
    """
    def perform_create(self, serializer):
        """Дополнительная валидация при создании"""
        self.validate_create(serializer.validated_data)
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Дополнительная валидация при обновлении"""
        self.validate_update(serializer.validated_data, serializer.instance)
        super().perform_update(serializer)
    
    def validate_create(self, validated_data):
        """Переопределите этот метод для валидации создания"""
        pass
    
    def validate_update(self, validated_data, instance):
        """Переопределите этот метод для валидации обновления"""
        pass


class BulkActionMixin:
    """
    Миксин для массовых операций
    """
    def get_bulk_queryset(self, ids):
        """Получает queryset для массовых операций"""
        queryset = self.get_queryset()
        return queryset.filter(id__in=ids)
    
    def bulk_delete(self, request):
        """Массовое удаление"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'Не указаны ID объектов'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_bulk_queryset(ids)
        deleted_count = queryset.count()
        
        for instance in queryset:
            self.perform_destroy(instance)
        
        return Response({
            'message': f'Удалено объектов: {deleted_count}',
            'deleted_count': deleted_count
        })
    
    def bulk_update(self, request):
        """Массовое обновление"""
        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        
        if not ids:
            return Response({'error': 'Не указаны ID объектов'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not update_data:
            return Response({'error': 'Не указаны данные для обновления'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_bulk_queryset(ids)
        updated_count = queryset.update(**update_data, updated_at=timezone.now())
        
        return Response({
            'message': f'Обновлено объектов: {updated_count}',
            'updated_count': updated_count
        })


class StatisticsMixin:
    """
    Миксин для добавления статистики к ответам
    """
    include_stats = False
    
    def list(self, request, *args, **kwargs):
        """Добавляет статистику к списку объектов"""
        response = super().list(request, *args, **kwargs)
        
        if self.include_stats:
            stats = self.get_statistics(response.data.get('results', response.data))
            if hasattr(response.data, 'get') and 'results' in response.data:
                response.data['statistics'] = stats
            else:
                response.data = {
                    'results': response.data,
                    'statistics': stats
                }
        
        return response
    
    def get_statistics(self, data):
        """Переопределите для вычисления статистики"""
        return {
            'total_items': len(data) if isinstance(data, list) else 0
        }