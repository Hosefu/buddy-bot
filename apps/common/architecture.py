"""
Базовые классы для единой архитектуры приложения
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response


@dataclass
class ServiceResult:
    """Результат выполнения сервисного метода"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    status_code: int = status.HTTP_200_OK


class BaseService(ABC):
    """Базовый класс для всех сервисов"""
    
    def execute(self, *args, **kwargs) -> ServiceResult:
        """Основной метод выполнения с обработкой ошибок"""
        try:
            with transaction.atomic():
                return self._execute(*args, **kwargs)
        except Exception as e:
            return self._handle_error(e)
    
    @abstractmethod
    def _execute(self, *args, **kwargs) -> ServiceResult:
        """Реализация бизнес-логики"""
        pass
    
    def _handle_error(self, error: Exception) -> ServiceResult:
        """Обработка ошибок"""
        error_mapping = {
            'ValidationError': ('Ошибка валидации', 'validation_error', 400),
            'PermissionDenied': ('Доступ запрещен', 'permission_denied', 403),
            'DoesNotExist': ('Объект не найден', 'not_found', 404),
            'IntegrityError': ('Ошибка целостности данных', 'integrity_error', 400),
        }
        
        error_type = error.__class__.__name__
        if error_type in error_mapping:
            message, code, status_code = error_mapping[error_type]
            return ServiceResult(
                success=False,
                error=message,
                error_code=code,
                status_code=status_code
            )
        
        # Для неизвестных ошибок
        return ServiceResult(
            success=False,
            error=str(error),
            error_code='internal_error',
            status_code=500
        ) 