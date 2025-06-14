"""
Кастомные валидаторы для системы онбординга
"""
import re
from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from typing import Any, Optional


@deconstructible
class TelegramUsernameValidator(BaseValidator):
    """
    Валидатор для Telegram username
    """
    message = _('Введите корректный Telegram username')
    code = 'invalid_telegram_username'
    
    def __call__(self, value):
        if not value:
            return
        
        # Убираем @ если есть
        username = value.lstrip('@')
        
        # Проверяем длину (5-32 символа)
        if len(username) < 5 or len(username) > 32:
            raise ValidationError(
                'Telegram username должен содержать от 5 до 32 символов',
                code=self.code
            )
        
        # Проверяем формат (буквы, цифры, подчеркивания)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError(
                'Telegram username может содержать только буквы, цифры и подчеркивания',
                code=self.code
            )
        
        # Не должен начинаться с цифры
        if username[0].isdigit():
            raise ValidationError(
                'Telegram username не может начинаться с цифры',
                code=self.code
            )


@deconstructible
class TelegramIdValidator(BaseValidator):
    """
    Валидатор для Telegram ID
    """
    message = _('Введите корректный Telegram ID')
    code = 'invalid_telegram_id'
    
    def __call__(self, value):
        if not value:
            return
        
        # Telegram ID должен быть числом
        try:
            telegram_id = int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                'Telegram ID должен быть числом',
                code=self.code
            )
        
        # Telegram ID должен быть положительным
        if telegram_id <= 0:
            raise ValidationError(
                'Telegram ID должен быть положительным числом',
                code=self.code
            )
        
        # Проверяем разумные границы (до 2^63-1)
        if telegram_id > 9223372036854775807:
            raise ValidationError(
                'Telegram ID слишком большой',
                code=self.code
            )


@deconstructible
class PasswordStrengthValidator:
    """
    Валидатор силы пароля
    """
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, 
                 require_digit=True, require_special=False):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
    
    def __call__(self, value):
        if len(value) < self.min_length:
            raise ValidationError(
                f'Пароль должен содержать минимум {self.min_length} символов',
                code='password_too_short'
            )
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            raise ValidationError(
                'Пароль должен содержать хотя бы одну заглавную букву',
                code='password_no_uppercase'
            )
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            raise ValidationError(
                'Пароль должен содержать хотя бы одну строчную букву',
                code='password_no_lowercase'
            )
        
        if self.require_digit and not re.search(r'\d', value):
            raise ValidationError(
                'Пароль должен содержать хотя бы одну цифру',
                code='password_no_digit'
            )
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(
                'Пароль должен содержать хотя бы один специальный символ',
                code='password_no_special'
            )


@deconstructible
class EmailDomainValidator:
    """
    Валидатор доменов email
    """
    def __init__(self, allowed_domains=None, blocked_domains=None):
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
    
    def __call__(self, value):
        if not value or '@' not in value:
            return
        
        domain = value.split('@')[1].lower()
        
        # Проверяем заблокированные домены
        if self.blocked_domains and domain in self.blocked_domains:
            raise ValidationError(
                f'Email с доменом {domain} не разрешен',
                code='email_domain_blocked'
            )
        
        # Проверяем разрешенные домены
        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValidationError(
                f'Разрешены только email с доменами: {", ".join(self.allowed_domains)}',
                code='email_domain_not_allowed'
            )


@deconstructible
class FileExtensionValidator:
    """
    Валидатор расширений файлов
    """
    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def __call__(self, value):
        if not value or not hasattr(value, 'name'):
            return
        
        if '.' not in value.name:
            raise ValidationError(
                'Файл должен иметь расширение',
                code='file_no_extension'
            )
        
        extension = value.name.split('.')[-1].lower()
        
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f'Разрешены только файлы с расширениями: {", ".join(self.allowed_extensions)}',
                code='file_extension_not_allowed'
            )


@deconstructible
class FileSizeValidator:
    """
    Валидатор размера файла
    """
    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def __call__(self, value):
        if not value or not hasattr(value, 'size'):
            return
        
        if value.size > self.max_size_bytes:
            raise ValidationError(
                f'Размер файла не должен превышать {self.max_size_mb} МБ',
                code='file_too_large'
            )


@deconstructible
class SlugValidator:
    """
    Валидатор для slug полей
    """
    def __call__(self, value):
        if not value:
            return
        
        # Slug должен содержать только буквы, цифры, дефисы и подчеркивания
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError(
                'Slug может содержать только буквы, цифры, дефисы и подчеркивания',
                code='invalid_slug'
            )
        
        # Не должен начинаться или заканчиваться дефисом
        if value.startswith('-') or value.endswith('-'):
            raise ValidationError(
                'Slug не может начинаться или заканчиваться дефисом',
                code='invalid_slug_format'
            )


@deconstructible
class JSONValidator:
    """
    Валидатор для JSON полей
    """
    def __init__(self, required_keys=None, allowed_keys=None):
        self.required_keys = required_keys or []
        self.allowed_keys = allowed_keys
    
    def __call__(self, value):
        if not isinstance(value, dict):
            raise ValidationError(
                'Значение должно быть объектом JSON',
                code='invalid_json'
            )
        
        # Проверяем обязательные ключи
        for key in self.required_keys:
            if key not in value:
                raise ValidationError(
                    f'Обязательный ключ "{key}" отсутствует',
                    code='missing_required_key'
                )
        
        # Проверяем разрешенные ключи
        if self.allowed_keys:
            for key in value.keys():
                if key not in self.allowed_keys:
                    raise ValidationError(
                        f'Ключ "{key}" не разрешен. Разрешенные ключи: {", ".join(self.allowed_keys)}',
                        code='key_not_allowed'
                    )


@deconstructible
class MarkdownValidator:
    """
    Валидатор для Markdown контента
    """
    def __init__(self, max_length=None, allowed_tags=None):
        self.max_length = max_length
        self.allowed_tags = allowed_tags or [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'strong', 'em', 'u', 'strike',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
            'a', 'img', 'table', 'tr', 'td', 'th'
        ]
    
    def __call__(self, value):
        if not value:
            return
        
        # Проверяем длину
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                f'Контент не должен превышать {self.max_length} символов',
                code='content_too_long'
            )
        
        # Проверяем на подозрительные теги (базовая проверка)
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'<iframe.*?>.*?</iframe>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                raise ValidationError(
                    'Контент содержит недопустимые элементы',
                    code='dangerous_content'
                )


@deconstructible
class PhoneNumberValidator:
    """
    Валидатор номеров телефонов
    """
    def __call__(self, value):
        if not value:
            return
        
        # Убираем все символы кроме цифр и +
        clean_number = re.sub(r'[^\d+]', '', value)
        
        # Проверяем формат
        if not re.match(r'^\+?[1-9]\d{7,14}$', clean_number):
            raise ValidationError(
                'Введите корректный номер телефона',
                code='invalid_phone_number'
            )


@deconstructible
class ColorHexValidator:
    """
    Валидатор для hex цветов
    """
    def __call__(self, value):
        if not value:
            return
        
        # Проверяем формат hex цвета
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise ValidationError(
                'Введите корректный hex цвет (например, #FF0000 или #F00)',
                code='invalid_hex_color'
            )


@deconstructible
class URLPathValidator:
    """
    Валидатор для URL путей
    """
    def __call__(self, value):
        if not value:
            return
        
        # URL путь должен начинаться с /
        if not value.startswith('/'):
            raise ValidationError(
                'URL путь должен начинаться с /',
                code='invalid_url_path'
            )
        
        # Проверяем на недопустимые символы
        if re.search(r'[<>"\s]', value):
            raise ValidationError(
                'URL путь содержит недопустимые символы',
                code='invalid_url_path_chars'
            )


def validate_quiz_passing_score(value):
    """
    Валидатор для проходного балла квиза
    """
    if value < 1 or value > 100:
        raise ValidationError(
            'Проходной балл должен быть от 1 до 100',
            code='invalid_passing_score'
        )


def validate_flow_order(value):
    """
    Валидатор для порядка этапов потока
    """
    if value < 1:
        raise ValidationError(
            'Порядок этапа должен быть положительным числом',
            code='invalid_flow_order'
        )


def validate_reading_time(value):
    """
    Валидатор для времени чтения
    """
    if value < 1 or value > 480:  # до 8 часов
        raise ValidationError(
            'Время чтения должно быть от 1 до 480 минут',
            code='invalid_reading_time'
        )


def validate_tags_list(value):
    """
    Валидатор для списка тегов
    """
    if not isinstance(value, list):
        raise ValidationError(
            'Теги должны быть списком',
            code='invalid_tags_format'
        )
    
    if len(value) > 10:
        raise ValidationError(
            'Количество тегов не должно превышать 10',
            code='too_many_tags'
        )
    
    for tag in value:
        if not isinstance(tag, str):
            raise ValidationError(
                'Каждый тег должен быть строкой',
                code='invalid_tag_type'
            )
        
        if len(tag) > 50:
            raise ValidationError(
                'Длина тега не должна превышать 50 символов',
                code='tag_too_long'
            )
        
        if not re.match(r'^[a-zA-Zа-яА-Я0-9_-]+$', tag):
            raise ValidationError(
                'Тег может содержать только буквы, цифры, дефисы и подчеркивания',
                code='invalid_tag_format'
            )


class TelegramValidator:
    """Валидатор данных Telegram"""
    
    @staticmethod
    def validate_telegram_id(value: str) -> str:
        """Валидация Telegram ID"""
        if not value or not value.isdigit():
            raise ValidationError("Неверный формат Telegram ID")
        return value
    
    @staticmethod
    def validate_username(value: str) -> str:
        """Валидация Telegram username"""
        if value and not re.match(r'^[a-zA-Z0-9_]{5,32}$', value):
            raise ValidationError("Неверный формат Telegram username")
        return value


class ContentValidator:
    """Валидатор контента"""
    
    @staticmethod
    def validate_title(value: str) -> str:
        """Валидация заголовка"""
        if not value or len(value.strip()) < 3:
            raise ValidationError("Заголовок должен содержать минимум 3 символа")
        if len(value) > 255:
            raise ValidationError("Заголовок не должен превышать 255 символов")
        return value.strip()
    
    @staticmethod
    def validate_content(value: str) -> str:
        """Валидация контента"""
        if not value or len(value.strip()) < 10:
            raise ValidationError("Контент должен содержать минимум 10 символов")
        return value.strip()
    
    @staticmethod
    def validate_summary(value: Optional[str]) -> Optional[str]:
        """Валидация краткого описания"""
        if value is not None:
            if len(value.strip()) < 10:
                raise ValidationError("Краткое описание должно содержать минимум 10 символов")
            if len(value) > 500:
                raise ValidationError("Краткое описание не должно превышать 500 символов")
            return value.strip()
        return None