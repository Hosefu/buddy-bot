"""
Основная конфигурация URL-ов проекта
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Админка Django
    path('django-admin/', admin.site.urls),
    
    # API документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API эндпоинты
    path('api/', include([
        # Авторизация и пользователи
        path('auth/', include('apps.users.urls')),
        
        # Мои данные и прогресс (для обычных пользователей)
        path('my/', include('apps.flows.urls')),
        
        # Buddy функционал
        path('buddy/', include('apps.flows.buddy_urls')),
        
        # Административные функции
        path('admin/', include('apps.flows.admin_urls')),
        
        # Общедоступные флоу и контент
        path('flows/', include('apps.flows.public_urls')),
        
        # Статьи и гайды
        path('articles/', include('apps.guides.urls')),
    ])),
]

# Добавляем статические и медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Настройка заголовков для административной панели
admin.site.site_header = "Telegram Onboarding Admin"
admin.site.site_title = "Telegram Onboarding"
admin.site.index_title = "Управление системой онбординга"
