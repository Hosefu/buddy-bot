"""
URL конфигурация для системы потоков обучения
Разделена на несколько файлов по группам пользователей
"""
from django.urls import path, include

app_name = 'flows'

# Основные URL разделены по ролям пользователей
urlpatterns = [
    # Эндпоинты для обычных пользователей (/api/my/)
    path('', include('apps.flows.user_urls')),
    
    # Эндпоинты для buddy (/api/buddy/)
    path('', include('apps.flows.buddy_urls')),
    
    # Эндпоинты для модераторов (/api/admin/)
    path('', include('apps.flows.admin_urls')),
    
    # Публичные эндпоинты потоков (/api/flows/)
    path('', include('apps.flows.public_urls')),
]