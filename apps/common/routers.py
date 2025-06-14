"""
Кастомные роутеры для API
"""
from rest_framework.routers import DefaultRouter
from django.urls import path
from typing import List, Tuple, Any


class VersionedRouter(DefaultRouter):
    """Роутер с поддержкой версионирования API"""
    
    def __init__(self, *args, version='v1', **kwargs):
        self.version = version
        super().__init__(*args, **kwargs)
    
    def get_urls(self):
        """Получение URL с версией"""
        urls = super().get_urls()
        return [
            path(f'{self.version}/{url.pattern}', url.callback, name=url.name)
            for url in urls
        ]


def register_viewsets(router: DefaultRouter, viewsets: List[Tuple[str, Any]]):
    """
    Регистрация множества viewsets
    
    Args:
        router: Роутер для регистрации
        viewsets: Список кортежей (prefix, viewset)
    """
    for prefix, viewset in viewsets:
        router.register(prefix, viewset, basename=prefix)


class NestedRouter(DefaultRouter):
    """Роутер с поддержкой вложенных ресурсов"""
    
    def __init__(self, *args, parent_prefix=None, parent_lookup_kwarg=None, **kwargs):
        self.parent_prefix = parent_prefix
        self.parent_lookup_kwarg = parent_lookup_kwarg
        super().__init__(*args, **kwargs)
    
    def get_urls(self):
        """Получение URL с учетом вложенности"""
        urls = super().get_urls()
        if self.parent_prefix and self.parent_lookup_kwarg:
            return [
                path(
                    f'{self.parent_prefix}/<{self.parent_lookup_kwarg}>/{url.pattern}',
                    url.callback,
                    name=url.name
                )
                for url in urls
            ]
        return urls 