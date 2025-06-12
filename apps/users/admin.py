"""
Административная панель для пользователей
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse

from .models import User, Role, UserRole, TelegramSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Административная панель для пользователей
    """
    list_display = [
        'telegram_id', 'name', 'position', 'department', 
        'is_active', 'telegram_link_display', 'roles_display', 
        'last_login_at', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_staff', 'department', 'hire_date',
        'user_roles__role__name', 'created_at'
    ]
    search_fields = ['telegram_id', 'name', 'telegram_username', 'position']
    readonly_fields = ['created_at', 'updated_at', 'last_login_at', 'telegram_link']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('telegram_id', 'name', 'password')
        }),
        ('Telegram', {
            'fields': ('telegram_username', 'telegram_link')
        }),
        ('HR информация', {
            'fields': ('position', 'department', 'hire_date')
        }),
        ('Системные поля', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Временные метки', {
            'fields': ('last_login_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Создание пользователя', {
            'classes': ('wide',),
            'fields': ('telegram_id', 'name', 'password1', 'password2', 'position', 'department')
        }),
    )
    
    ordering = ['name']
    filter_horizontal = ['groups', 'user_permissions']
    
    def telegram_link_display(self, obj):
        """Отображение ссылки на Telegram"""
        if obj.telegram_link:
            return format_html(
                '<a href="{}" target="_blank">@{}</a>',
                obj.telegram_link,
                obj.telegram_username or obj.telegram_id
            )
        return '-'
    telegram_link_display.short_description = 'Telegram'
    
    def roles_display(self, obj):
        """Отображение ролей пользователя"""
        roles = obj.get_active_roles()
        if roles:
            role_links = []
            for user_role in roles:
                url = reverse('admin:users_userrole_change', args=[user_role.id])
                role_links.append(
                    format_html('<a href="{}">{}</a>', url, user_role.role.display_name)
                )
            return format_html(', '.join(role_links))
        return '-'
    roles_display.short_description = 'Роли'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related().prefetch_related('user_roles__role')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Административная панель для ролей
    """
    list_display = ['display_name', 'name', 'users_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'name', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def users_count(self, obj):
        """Количество пользователей с ролью"""
        return obj.role_users.filter(is_active=True).count()
    users_count.short_description = 'Пользователей'


class UserRoleInline(admin.TabularInline):
    """
    Инлайн для ролей пользователя
    """
    model = UserRole
    extra = 0
    readonly_fields = ['assigned_at', 'created_at']
    fields = ['role', 'is_active', 'assigned_by', 'assigned_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role', 'assigned_by')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Административная панель для связей пользователь-роль
    """
    list_display = [
        'user_name', 'role_name', 'is_active', 
        'assigned_by_name', 'assigned_at'
    ]
    list_filter = ['is_active', 'role__name', 'assigned_at']
    search_fields = ['user__name', 'user__email', 'role__display_name']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Назначение роли', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Информация о назначении', {
            'fields': ('assigned_by', 'assigned_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.name
    user_name.short_description = 'Пользователь'
    user_name.admin_order_field = 'user__name'
    
    def role_name(self, obj):
        return obj.role.display_name
    role_name.short_description = 'Роль'
    role_name.admin_order_field = 'role__display_name'
    
    def assigned_by_name(self, obj):
        return obj.assigned_by.name if obj.assigned_by else '-'
    assigned_by_name.short_description = 'Назначил'
    assigned_by_name.admin_order_field = 'assigned_by__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'role', 'assigned_by')


@admin.register(TelegramSession)
class TelegramSessionAdmin(admin.ModelAdmin):
    """
    Административная панель для Telegram сессий
    """
    list_display = [
        'user_name', 'auth_date', 'expires_at', 
        'is_valid', 'is_expired_display'
    ]
    list_filter = ['is_valid', 'auth_date', 'expires_at']
    search_fields = ['user__name', 'user__email', 'user__telegram_id']
    readonly_fields = ['auth_date', 'created_at', 'updated_at', 'is_expired_display']
    
    fieldsets = (
        ('Сессия', {
            'fields': ('user', 'is_valid', 'auth_date', 'expires_at')
        }),
        ('Telegram данные', {
            'fields': ('telegram_data', 'hash_value'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('is_expired_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.name
    user_name.short_description = 'Пользователь'
    user_name.admin_order_field = 'user__name'
    
    def is_expired_display(self, obj):
        """Отображение истекшей сессии"""
        if obj.is_expired():
            return format_html('<span style="color: red;">Истекла</span>')
        return format_html('<span style="color: green;">Активна</span>')
    is_expired_display.short_description = 'Статус'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Дополнительные настройки админки
admin.site.site_header = "Telegram Onboarding Admin"
admin.site.site_title = "Telegram Onboarding"
admin.site.index_title = "Управление системой онбординга"