"""
Утилиты для кэширования
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json
from typing import Any, Optional, Callable


def cache_result(timeout: int = 300, key_prefix: Optional[str] = None, vary_on_user: bool = False):
    """
    Декоратор для кэширования результатов функций/методов
    
    Args:
        timeout: Время жизни кэша в секундах
        key_prefix: Префикс для ключа кэша
        vary_on_user: Различать кэш для разных пользователей
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Формируем ключ кэша
            cache_key_parts = [
                key_prefix or f"{func.__module__}.{func.__name__}",
            ]
            
            # Добавляем user_id если нужно
            if vary_on_user and hasattr(args[0], 'user'):
                cache_key_parts.append(f"user_{args[0].user.id}")
            
            # Добавляем аргументы функции
            if args[1:]:  # Пропускаем self/cls
                args_str = hashlib.md5(
                    json.dumps(args[1:], sort_keys=True).encode()
                ).hexdigest()[:8]
                cache_key_parts.append(args_str)
            
            if kwargs:
                kwargs_str = hashlib.md5(
                    json.dumps(kwargs, sort_keys=True).encode()
                ).hexdigest()[:8]
                cache_key_parts.append(kwargs_str)
            
            cache_key = ":".join(cache_key_parts)
            
            # Пытаемся получить из кэша
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Вычисляем результат
            result = func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache.set(cache_key, result, timeout)
            
            return result
        
        # Добавляем метод для инвалидации кэша
        def invalidate(*args, **kwargs):
            cache_key_parts = [
                key_prefix or f"{func.__module__}.{func.__name__}",
            ]
            # Формируем паттерн для удаления
            pattern = ":".join(cache_key_parts) + "*"
            cache.delete_pattern(pattern)
        
        wrapper.invalidate = invalidate
        return wrapper
    return decorator


def cache_page_data(timeout: int = 300):
    """Декоратор для кэширования данных страниц ViewSet"""
    def decorator(viewset_method: Callable) -> Callable:
        @wraps(viewset_method)
        def wrapper(self, request, *args, **kwargs):
            # Формируем ключ с учетом параметров запроса
            cache_key = f"view:{request.path}:{request.query_params.urlencode()}"
            
            if request.user.is_authenticated:
                cache_key += f":user_{request.user.id}"
            
            # Пытаемся получить из кэша
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Получаем ответ
            response = viewset_method(self, request, *args, **kwargs)
            
            # Кэшируем только успешные GET запросы
            if request.method == 'GET' and response.status_code == 200:
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def cache_model_method(timeout: int = 300):
    """Декоратор для кэширования методов моделей"""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Формируем ключ кэша
            cache_key = f"model:{self.__class__.__name__}:{self.id}:{method.__name__}"
            
            # Пытаемся получить из кэша
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Вычисляем результат
            result = method(self, *args, **kwargs)
            
            # Сохраняем в кэш
            cache.set(cache_key, result, timeout)
            
            return result
        
        # Добавляем метод для инвалидации кэша
        def invalidate(self):
            cache_key = f"model:{self.__class__.__name__}:{self.id}:{method.__name__}"
            cache.delete(cache_key)
        
        wrapper.invalidate = invalidate
        return wrapper
    return decorator 