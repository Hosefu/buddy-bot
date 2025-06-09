"""
Кастомные исключения для системы онбординга
"""
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class OnboardingBaseException(Exception):
    """
    Базовое исключение для системы онбординга
    """
    default_message = "Произошла ошибка в системе онбординга"
    default_code = "onboarding_error"
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message=None, code=None, extra_data=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.extra_data = extra_data or {}
        super().__init__(self.message)


class UserNotFoundError(OnboardingBaseException):
    """
    Исключение для случаев, когда пользователь не найден
    """
    default_message = "Пользователь не найден"
    default_code = "user_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class UserInactiveError(OnboardingBaseException):
    """
    Исключение для неактивных пользователей
    """
    default_message = "Пользователь неактивен"
    default_code = "user_inactive"
    status_code = status.HTTP_403_FORBIDDEN


class InsufficientPermissionsError(OnboardingBaseException):
    """
    Исключение для недостаточных прав доступа
    """
    default_message = "Недостаточно прав для выполнения действия"
    default_code = "insufficient_permissions"
    status_code = status.HTTP_403_FORBIDDEN


class FlowNotFoundError(OnboardingBaseException):
    """
    Исключение когда поток обучения не найден
    """
    default_message = "Поток обучения не найден"
    default_code = "flow_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class FlowAlreadyAssignedError(OnboardingBaseException):
    """
    Исключение когда поток уже назначен пользователю
    """
    default_message = "Поток обучения уже назначен пользователю"
    default_code = "flow_already_assigned"
    status_code = status.HTTP_409_CONFLICT


class FlowStepNotAccessibleError(OnboardingBaseException):
    """
    Исключение когда этап потока недоступен
    """
    default_message = "Этап потока недоступен для выполнения"
    default_code = "flow_step_not_accessible"
    status_code = status.HTTP_403_FORBIDDEN


class FlowStepNotCompletedError(OnboardingBaseException):
    """
    Исключение когда требуется завершить предыдущий этап
    """
    default_message = "Необходимо завершить предыдущий этап"
    default_code = "flow_step_not_completed"
    status_code = status.HTTP_400_BAD_REQUEST


class QuizFailedError(OnboardingBaseException):
    """
    Исключение когда квиз не пройден
    """
    default_message = "Квиз не пройден. Недостаточно правильных ответов"
    default_code = "quiz_failed"
    status_code = status.HTTP_400_BAD_REQUEST


class TaskAnswerIncorrectError(OnboardingBaseException):
    """
    Исключение когда ответ на задание неверен
    """
    default_message = "Неверный ответ на задание"
    default_code = "task_answer_incorrect"
    status_code = status.HTTP_400_BAD_REQUEST


class ArticleNotFoundError(OnboardingBaseException):
    """
    Исключение когда статья не найдена
    """
    default_message = "Статья не найдена"
    default_code = "article_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ArticleNotPublishedError(OnboardingBaseException):
    """
    Исключение когда статья не опубликована
    """
    default_message = "Статья не опубликована"
    default_code = "article_not_published"
    status_code = status.HTTP_403_FORBIDDEN


class TelegramAuthenticationError(OnboardingBaseException):
    """
    Исключение для ошибок аутентификации Telegram
    """
    default_message = "Ошибка аутентификации Telegram"
    default_code = "telegram_auth_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class TelegramDataValidationError(OnboardingBaseException):
    """
    Исключение для ошибок валидации данных Telegram
    """
    default_message = "Неверные данные от Telegram"
    default_code = "telegram_data_invalid"
    status_code = status.HTTP_400_BAD_REQUEST


class BuddyNotAssignedError(OnboardingBaseException):
    """
    Исключение когда бадди не назначен для потока
    """
    default_message = "Бадди не назначен для данного потока"
    default_code = "buddy_not_assigned"
    status_code = status.HTTP_403_FORBIDDEN


class FlowCannotBePausedError(OnboardingBaseException):
    """
    Исключение когда поток нельзя приостановить
    """
    default_message = "Поток нельзя приостановить в текущем состоянии"
    default_code = "flow_cannot_be_paused"
    status_code = status.HTTP_400_BAD_REQUEST


class FlowCannotBeResumedError(OnboardingBaseException):
    """
    Исключение когда поток нельзя возобновить
    """
    default_message = "Поток нельзя возобновить в текущем состоянии"
    default_code = "flow_cannot_be_resumed"
    status_code = status.HTTP_400_BAD_REQUEST


class ValidationError(OnboardingBaseException):
    """
    Общее исключение для ошибок валидации
    """
    default_message = "Ошибка валидации данных"
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class RateLimitExceededError(OnboardingBaseException):
    """
    Исключение при превышении лимита запросов
    """
    default_message = "Превышен лимит запросов. Попробуйте позже"
    default_code = "rate_limit_exceeded"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class ExternalServiceError(OnboardingBaseException):
    """
    Исключение для ошибок внешних сервисов
    """
    default_message = "Ошибка внешнего сервиса"
    default_code = "external_service_error"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class FileUploadError(OnboardingBaseException):
    """
    Исключение для ошибок загрузки файлов
    """
    default_message = "Ошибка загрузки файла"
    default_code = "file_upload_error"
    status_code = status.HTTP_400_BAD_REQUEST


class ConfigurationError(OnboardingBaseException):
    """
    Исключение для ошибок конфигурации
    """
    default_message = "Ошибка конфигурации системы"
    default_code = "configuration_error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF
    """
    # Вызываем стандартный обработчик
    response = exception_handler(exc, context)
    
    # Если это наше кастомное исключение
    if isinstance(exc, OnboardingBaseException):
        custom_response_data = {
            'error': {
                'code': exc.code,
                'message': exc.message,
                'details': exc.extra_data
            }
        }
        
        # Логируем ошибку
        request = context.get('request')
        logger.error(f"OnboardingException: {exc.code} - {exc.message}", extra={
            'user_id': request.user.id if request and request.user.is_authenticated else None,
            'path': request.path if request else None,
            'method': request.method if request else None,
            'exception_class': exc.__class__.__name__
        })
        
        return Response(custom_response_data, status=exc.status_code)
    
    # Если это стандартное исключение DRF и есть response
    if response is not None:
        # Стандартизируем формат ответа
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                # ValidationError или подобные
                custom_response_data = {
                    'error': {
                        'code': 'validation_error',
                        'message': str(response.data['detail']),
                        'details': {}
                    }
                }
            else:
                # Ошибки полей формы
                custom_response_data = {
                    'error': {
                        'code': 'validation_error',
                        'message': 'Ошибка валидации данных',
                        'details': response.data
                    }
                }
        else:
            custom_response_data = {
                'error': {
                    'code': 'unknown_error',
                    'message': str(response.data),
                    'details': {}
                }
            }
        
        response.data = custom_response_data
    
    # Логируем необработанные исключения
    else:
        logger.error(f"Unhandled exception: {exc}", extra={
            'exception_class': exc.__class__.__name__,
            'context': context
        })
    
    return response


class ErrorCodes:
    """
    Константы кодов ошибок
    """
    # Пользователи
    USER_NOT_FOUND = "user_not_found"
    USER_INACTIVE = "user_inactive"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    
    # Потоки обучения
    FLOW_NOT_FOUND = "flow_not_found"
    FLOW_ALREADY_ASSIGNED = "flow_already_assigned"
    FLOW_STEP_NOT_ACCESSIBLE = "flow_step_not_accessible"
    FLOW_STEP_NOT_COMPLETED = "flow_step_not_completed"
    FLOW_CANNOT_BE_PAUSED = "flow_cannot_be_paused"
    FLOW_CANNOT_BE_RESUMED = "flow_cannot_be_resumed"
    
    # Квизы и задания
    QUIZ_FAILED = "quiz_failed"
    TASK_ANSWER_INCORRECT = "task_answer_incorrect"
    
    # Статьи
    ARTICLE_NOT_FOUND = "article_not_found"
    ARTICLE_NOT_PUBLISHED = "article_not_published"
    
    # Telegram
    TELEGRAM_AUTH_ERROR = "telegram_auth_error"
    TELEGRAM_DATA_INVALID = "telegram_data_invalid"
    
    # Бадди
    BUDDY_NOT_ASSIGNED = "buddy_not_assigned"
    
    # Общие
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    FILE_UPLOAD_ERROR = "file_upload_error"
    CONFIGURATION_ERROR = "configuration_error"


class ErrorMessages:
    """
    Константы сообщений об ошибках
    """
    # Пользователи
    USER_NOT_FOUND = "Пользователь не найден"
    USER_INACTIVE = "Пользователь неактивен"
    INSUFFICIENT_PERMISSIONS = "Недостаточно прав для выполнения действия"
    
    # Потоки обучения
    FLOW_NOT_FOUND = "Поток обучения не найден"
    FLOW_ALREADY_ASSIGNED = "Поток обучения уже назначен пользователю"
    FLOW_STEP_NOT_ACCESSIBLE = "Этап потока недоступен для выполнения"
    FLOW_STEP_NOT_COMPLETED = "Необходимо завершить предыдущий этап"
    
    # Квизы и задания
    QUIZ_FAILED = "Квиз не пройден. Недостаточно правильных ответов"
    TASK_ANSWER_INCORRECT = "Неверный ответ на задание"
    
    # Статьи
    ARTICLE_NOT_FOUND = "Статья не найдена"
    ARTICLE_NOT_PUBLISHED = "Статья не опубликована"
    
    # Telegram
    TELEGRAM_AUTH_ERROR = "Ошибка аутентификации Telegram"
    TELEGRAM_DATA_INVALID = "Неверные данные от Telegram"
    
    # Общие
    VALIDATION_ERROR = "Ошибка валидации данных"
    RATE_LIMIT_EXCEEDED = "Превышен лимит запросов. Попробуйте позже"