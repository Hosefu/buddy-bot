"""
Основная URL конфигурация проекта онбординга
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),
    
    # API эндпоинты
    path('api/', include([
        # Авторизация и пользователи
        path('auth/', include('apps.users.urls')),
        
        # Мои данные и прогресс (для обычных пользователей)
        path('my/', include('apps.flows.user_urls')),
        
        # Buddy функционал
        path('buddy/', include('apps.flows.buddy_urls')),
        
        # Административные функции
        path('admin/', include('apps.flows.admin_urls')),
        
        # Общедоступные флоу и контент
        path('flows/', include('apps.flows.public_urls')),
        
        # Статьи и гайды
        path('articles/', include('apps.guides.urls')),
        
        # Webhook для Telegram бота
        path('webhook/', include('apps.users.urls.webhook_urls')),

        # API для бота
        path('bot/', include('apps.users.urls.bot_urls')),
    ])),
    
    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Настройки для медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Добавляем Debug Toolbar в режиме разработки
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Настройка заголовков для административной панели
admin.site.site_header = "Telegram Onboarding Admin"
admin.site.site_title = "Telegram Onboarding"
admin.site.index_title = "Управление системой онбординга"
