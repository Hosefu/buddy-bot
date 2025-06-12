"""
Представления для пользователей и аутентификации
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import transaction

from .models import User, Role, UserRole
from .serializers import (
    UserSerializer, UserCreateSerializer, UserDetailSerializer,
    TelegramAuthSerializer, UserRoleAssignSerializer, ProfileSerializer,
    PasswordChangeSerializer, UserListSerializer
)
from apps.common.permissions import (
    IsModerator, IsActiveUser, CanManageUserRoles,
    TelegramBotPermission
)


class TelegramAuthView(APIView):
    """
    Аутентификация через Telegram Mini App
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Авторизация пользователя через данные Telegram
        
        Body:
        {
            "id": "123456789",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "auth_date": "1234567890",
            "hash": "abcdef..."
        }
        """
        serializer = TelegramAuthSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Создаем или обновляем пользователя
                user = serializer.create_or_update_user(serializer.validated_data)
                
                # Генерируем JWT токены
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Обновляем время последнего входа
                user.last_login_at = timezone.now()
                user.save(update_fields=['last_login_at'])
                
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Ошибка авторизации',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление информации о текущем пользователе
    """
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser]
    
    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и редактирование профиля пользователя
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsActiveUser]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    Смена пароля пользователя
    """
    permission_classes = [IsActiveUser]
    
    def post(self, request):
        """
        Смена пароля
        
        Body:
        {
            "old_password": "old_password",
            "new_password": "new_password",
            "new_password_confirm": "new_password"
        }
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Пароль успешно изменен'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListCreateAPIView):
    """
    Список пользователей и создание новых (только для модераторов)
    """
    queryset = User.objects.active_users().order_by('name')
    permission_classes = [IsModerator]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer
    
    def get_queryset(self):
        """Фильтрация пользователей"""
        queryset = super().get_queryset()
        
        # Фильтр по отделу
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # Фильтр по роли
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(
                user_roles__role__name=role,
                user_roles__is_active=True
            ).distinct()
        
        # Поиск по имени или telegram_id
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(telegram_id__icontains=search) |
                models.Q(telegram_username__icontains=search)
            )
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Подробная информация о пользователе (только для модераторов)
    """
    queryset = User.objects.active_users()
    serializer_class = UserDetailSerializer
    permission_classes = [IsModerator]
    
    def destroy(self, request, *args, **kwargs):
        """Мягкое удаление пользователя"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleAssignView(APIView):
    """
    Назначение и отзыв ролей пользователей
    """
    permission_classes = [CanManageUserRoles]
    
    def post(self, request, user_id):
        """
        Назначение роли пользователю
        
        Body:
        {
            "role_id": 1
        }
        """
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({
                'error': 'Пользователь не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserRoleAssignSerializer(
            data={**request.data, 'user_id': user_id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            user_role = serializer.save()
            return Response({
                'message': f'Роль {user_role.role.display_name} назначена пользователю {user.name}',
                'user_role': {
                    'id': user_role.id,
                    'role': user_role.role.display_name,
                    'assigned_at': user_role.assigned_at
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id, role_id):
        """
        Отзыв роли у пользователя
        """
        try:
            user = User.objects.get(id=user_id, is_active=True)
            role = Role.objects.get(id=role_id, is_active=True)
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({
                'error': 'Пользователь или роль не найдены'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user_role = UserRole.objects.get(
                user=user,
                role=role,
                is_active=True
            )
            user_role.is_active = False
            user_role.save()
            
            return Response({
                'message': f'Роль {role.display_name} отозвана у пользователя {user.name}'
            }, status=status.HTTP_200_OK)
            
        except UserRole.DoesNotExist:
            return Response({
                'error': 'Пользователь не имеет указанной роли'
            }, status=status.HTTP_404_NOT_FOUND)


class RoleListView(generics.ListAPIView):
    """
    Список доступных ролей
    """
    from .serializers import RoleSerializer
    
    queryset = Role.objects.filter(is_active=True).order_by('display_name')
    serializer_class = RoleSerializer
    permission_classes = [IsModerator]


class BuddyListView(generics.ListAPIView):
    """
    Список пользователей с ролью buddy (для назначения)
    """
    serializer_class = UserListSerializer
    permission_classes = [IsModerator]
    
    def get_queryset(self):
        return User.objects.buddies().order_by('name')


# Webhook и Bot API для Telegram
class TelegramWebhookView(APIView):
    """
    Обработка webhook от Telegram бота
    """
    permission_classes = [permissions.AllowAny]  # Валидация внутри
    
    def post(self, request):
        """
        Обработка обновлений от Telegram
        """
        # Здесь должна быть валидация webhook от Telegram
        # и обработка различных типов обновлений
        
        update_data = request.data
        
        # Базовая обработка (расширить при необходимости)
        if 'message' in update_data:
            message = update_data['message']
            user_id = message.get('from', {}).get('id')
            
            if user_id:
                # Обновляем информацию о последней активности пользователя
                try:
                    user = User.objects.get_by_telegram_id(str(user_id))
                    if user:
                        user.last_login_at = timezone.now()
                        user.save(update_fields=['last_login_at'])
                except Exception:
                    pass  # Пользователь не найден в системе
        
        return Response({'ok': True}, status=status.HTTP_200_OK)


class BotUserInfoView(APIView):
    """
    API для получения информации о пользователе ботом
    """
    permission_classes = [TelegramBotPermission]
    
    def get(self, request, telegram_id):
        """
        Получение информации о пользователе по Telegram ID
        """
        try:
            user = User.objects.get_by_telegram_id(telegram_id)
            if not user:
                return Response({
                    'error': 'Пользователь не найден'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Получаем активные потоки пользователя
            from apps.flows.models import UserFlow
            active_flows = UserFlow.objects.filter(
                user=user,
                status__in=['not_started', 'in_progress']
            ).select_related('flow')
            
            return Response({
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'position': user.position,
                    'department': user.department
                },
                'active_flows': [
                    {
                        'id': uf.id,
                        'flow_title': uf.flow.title,
                        'status': uf.status,
                        'progress_percentage': uf.progress_percentage,
                        'expected_completion_date': uf.expected_completion_date
                    }
                    for uf in active_flows
                ]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка получения информации о пользователе',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def telegram_mini_app_auth(request):
    """
    Упрощенная аутентификация для Telegram Mini App
    (альтернативный эндпоинт с простой структурой)
    """
    telegram_data = request.data
    
    # Базовая валидация
    required_fields = ['id', 'first_name', 'auth_date', 'hash']
    if not all(field in telegram_data for field in required_fields):
        return Response({
            'error': 'Недостаточно данных для авторизации'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Простая авторизация без глубокой валидации
        # (для разработки, в продакшене нужна полная валидация)
        telegram_id = str(telegram_data['id'])
        name = telegram_data['first_name']
        
        if 'last_name' in telegram_data:
            name += f" {telegram_data['last_name']}"
        
        # Ищем или создаем пользователя
        user = User.objects.get_by_telegram_id(telegram_id)
        
        if not user:
            user = User.objects.create_telegram_user(
                telegram_id=telegram_id,
                name=name,
                telegram_username=telegram_data.get('username', '')
            )
            
            # Назначаем базовую роль, если она ещё не присвоена
            try:
                user_role = Role.objects.get(name='user')
                UserRole.objects.get_or_create(user=user, role=user_role)
            except Role.DoesNotExist:
                pass
        
        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Ошибка авторизации: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)