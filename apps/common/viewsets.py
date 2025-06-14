"""
Базовые классы для ViewSets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .responses import APIResponse
from .permissions import require_role


class BaseViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с общей функциональностью"""
    
    def get_serializer_context(self):
        """Добавляем request в контекст"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def handle_exception(self, exc):
        """Централизованная обработка исключений"""
        if isinstance(exc, ValidationError):
            return APIResponse.error(
                message=str(exc),
                error_code='validation_error',
                status_code=400
            )
        return super().handle_exception(exc)
    
    def perform_create(self, serializer):
        """Создание объекта с контекстом"""
        serializer.save(**self.get_extra_data())
    
    def perform_update(self, serializer):
        """Обновление объекта с контекстом"""
        serializer.save(**self.get_extra_data())
    
    def get_extra_data(self):
        """Дополнительные данные для сохранения"""
        return {}


class ReadOnlyViewSet(BaseViewSet):
    """ViewSet только для чтения"""
    http_method_names = ['get', 'head', 'options']


class BulkViewSet(BaseViewSet):
    """ViewSet с поддержкой bulk операций"""
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Массовое создание объектов"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )
    
    def perform_bulk_create(self, serializer):
        """Выполнение массового создания"""
        serializer.save(**self.get_extra_data())
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """Массовое обновление объектов"""
        serializer = self.get_serializer(
            self.get_queryset(),
            data=request.data,
            many=True,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return APIResponse.success(data=serializer.data)
    
    def perform_bulk_update(self, serializer):
        """Выполнение массового обновления"""
        serializer.save(**self.get_extra_data())
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Массовое удаление объектов"""
        ids = request.data.get('ids', [])
        deleted_count = self.get_queryset().filter(id__in=ids).delete()[0]
        return APIResponse.success(
            data={'deleted': deleted_count},
            message=f'Удалено объектов: {deleted_count}'
        ) 