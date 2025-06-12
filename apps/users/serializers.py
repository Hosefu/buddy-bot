"""
Сериализаторы для пользователей и аутентификации
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import hashlib
import hmac

from .models import User, Role, UserRole, TelegramSession


class RoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ролей
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description']
        read_only_fields = ['id']


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи пользователь-роль
    """
    role = RoleSerializer(read_only=True)
    assigned_by_name = serializers.CharField(
        source='assigned_by.name', 
        read_only=True
    )
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'role', 'assigned_by_name', 'assigned_at', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор пользователя
    """
    active_roles = UserRoleSerializer(
        source='get_active_roles', 
        many=True, 
        read_only=True
    )
    telegram_link = serializers.URLField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'telegram_id', 'name', 'telegram_username',
            'position', 'department', 'hire_date', 'is_active',
            'last_login_at', 'created_at', 'active_roles', 'telegram_link'
        ]
        read_only_fields = [
            'id', 'telegram_id', 'last_login_at', 'created_at', 
            'telegram_link'
        ]
    
    def validate_telegram_id(self, value):
        """Валидация Telegram ID"""
        if not value:
            raise serializers.ValidationError("Telegram ID обязателен")
        
        # Проверяем уникальность
        if User.objects.filter(telegram_id=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("Пользователь с таким Telegram ID уже существует")
        
        return str(value).strip()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'telegram_id', 'name', 'password', 'password_confirm',
            'position', 'department', 'hire_date'
        ]
    
    def validate(self, data):
        """Валидация паролей"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
    
    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserDetailSerializer(UserSerializer):
    """
    Подробный сериализатор пользователя для административных функций
    """
    user_roles = UserRoleSerializer(many=True, read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'user_roles', 'telegram_username', 'updated_at'
        ]


class TelegramAuthSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации через Telegram Mini App
    """
    # Данные от Telegram
    id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    auth_date = serializers.CharField()
    hash = serializers.CharField()
    
    def validate(self, data):
        """
        Валидация данных от Telegram
        Проверяет подпись данных с помощью секретного ключа бота
        """
        from django.conf import settings
        
        # Получаем секретный ключ бота
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            raise serializers.ValidationError("Telegram bot token не настроен")
        
        # Создаем строку для проверки подписи
        received_hash = data.pop('hash')
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data.items()) if v])
        
        # Создаем секретный ключ
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Вычисляем ожидаемый хеш
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем подпись
        if not hmac.compare_digest(expected_hash, received_hash):
            raise serializers.ValidationError("Неверная подпись данных Telegram")
        
        # Проверяем время авторизации (не старше 1 дня)
        auth_timestamp = int(data['auth_date'])
        current_timestamp = timezone.now().timestamp()
        
        if current_timestamp - auth_timestamp > 86400:  # 24 часа
            raise serializers.ValidationError("Данные авторизации устарели")
        
        # Возвращаем данные с восстановленным хешем
        data['hash'] = received_hash
        return data
    
    def create_or_update_user(self, validated_data):
        """
        Создает или обновляет пользователя на основе данных Telegram
        """
        telegram_id = validated_data['id']
        
        # Формируем полное имя
        full_name = validated_data['first_name']
        if validated_data.get('last_name'):
            full_name += f" {validated_data['last_name']}"
        
        # Пытаемся найти существующего пользователя
        user = User.objects.get_by_telegram_id(telegram_id)
        
        if user:
            # Обновляем данные существующего пользователя
            user.name = full_name
            user.telegram_username = validated_data.get('username', '')
            user.last_login_at = timezone.now()
            user.save()
        else:
            # Создаем нового пользователя
            user = User.objects.create_telegram_user(
                telegram_id=telegram_id,
                name=full_name,
                telegram_username=validated_data.get('username', '')
            )
            
            # Назначаем базовую роль "user"
            try:
                user_role = Role.objects.get(name='user')
                UserRole.objects.create(
                    user=user,
                    role=user_role,
                    assigned_by=None
                )
            except Role.DoesNotExist:
                pass
        
        # Создаем или обновляем Telegram сессию
        auth_date = timezone.datetime.fromtimestamp(
            int(validated_data['auth_date']),
            tz=timezone.get_current_timezone()
        )
        
        TelegramSession.objects.update_or_create(
            user=user,
            defaults={
                'telegram_data': validated_data,
                'auth_date': auth_date,
                'hash_value': validated_data['hash'],
                'is_valid': True,
                'expires_at': timezone.now() + timedelta(days=7)
            }
        )
        
        return user


class UserRoleAssignSerializer(serializers.Serializer):
    """
    Сериализатор для назначения роли пользователю
    """
    role_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    
    def validate_role_id(self, value):
        """Валидация роли"""
        try:
            role = Role.objects.get(id=value, is_active=True)
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError("Роль не найдена")
    
    def validate_user_id(self, value):
        """Валидация пользователя"""
        try:
            user = User.objects.get(id=value, is_active=True)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
    
    def validate(self, data):
        """Валидация назначения роли"""
        role = data['role_id']
        user = data['user_id']
        
        # Проверяем, не назначена ли уже эта роль
        if UserRole.objects.filter(user=user, role=role, is_active=True).exists():
            raise serializers.ValidationError(
                f"Пользователь уже имеет роль {role.display_name}"
            )
        
        return data
    
    def create(self, validated_data):
        """Назначение роли пользователю"""
        return UserRole.objects.create(
            user=validated_data['user_id'],
            role=validated_data['role_id'],
            assigned_by=self.context['request'].user
        )


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя (для самого пользователя)
    """
    active_roles = serializers.StringRelatedField(
        source='get_active_roles', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'telegram_username',
            'position', 'department', 'hire_date', 
            'active_roles', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'active_roles']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        """Валидация старого пароля"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный старый пароль")
        return value
    
    def validate(self, data):
        """Валидация новых паролей"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают")
        return data
    
    def save(self):
        """Сохранение нового пароля"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка пользователей (краткая информация)
    """
    roles = serializers.StringRelatedField(
        source='get_active_roles',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'telegram_id', 'position', 'department', 
            'is_active', 'roles', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']