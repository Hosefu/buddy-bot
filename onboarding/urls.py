"""
�������� ������������ URL-�� �������
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ������� Django
    path('django-admin/', admin.site.urls),
    
    # API ������������
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API ���������
    path('api/', include([
        # ����������� � ������������
        path('auth/', include('apps.users.urls')),
        
        # ��� ������ � �������� (��� ������� �������������)
        path('my/', include('apps.flows.urls')),
        
        # Buddy ����������
        path('buddy/', include('apps.flows.buddy_urls')),
        
        # ���������������� �������
        path('admin/', include('apps.flows.admin_urls')),
        
        # ������������� ���� � �������
        path('flows/', include('apps.flows.public_urls')),
        
        # ������ � �����
        path('articles/', include('apps.guides.urls')),
    ])),
]

# ��������� ����������� � ����� ����� � ������ ����������
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ��������� ���������� ��� ���������������� ������
admin.site.site_header = "Telegram Onboarding Admin"
admin.site.site_title = "Telegram Onboarding"
admin.site.index_title = "���������� �������� ����������"
