"""
Общие утилиты и вспомогательные функции
"""
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import WorkingCalendar


def generate_random_string(length: int = 10, include_digits: bool = True, include_special: bool = False) -> str:
    """
    Генерирует случайную строку заданной длины
    
    Args:
        length: Длина строки
        include_digits: Включать цифры
        include_special: Включать специальные символы
        
    Returns:
        Случайная строка
    """
    characters = string.ascii_letters
    
    if include_digits:
        characters += string.digits
    
    if include_special:
        characters += "!@#$%^&*"
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Генерирует криптографически стойкий токен
    
    Args:
        length: Длина токена в байтах
        
    Returns:
        Токен в hex формате
    """
    return secrets.token_hex(length)


def validate_telegram_data(data: Dict[str, Any], bot_token: str) -> bool:
    """
    Валидирует данные от Telegram WebApp
    
    Args:
        data: Данные от Telegram
        bot_token: Токен бота
        
    Returns:
        True если данные валидны
    """
    if 'hash' not in data:
        return False
    
    received_hash = data.pop('hash')
    
    # Создаем строку для проверки
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
    return hmac.compare_digest(expected_hash, received_hash)


def format_duration(seconds: int) -> str:
    """
    Форматирует продолжительность в читаемый вид
    
    Args:
        seconds: Количество секунд
        
    Returns:
        Отформатированная строка
    """
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ч {minutes} мин"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} д {hours} ч"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Обрезает текст до заданной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
        
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Вычисляет время чтения текста
    
    Args:
        text: Текст для анализа
        words_per_minute: Скорость чтения слов в минуту
        
    Returns:
        Время чтения в минутах
    """
    word_count = len(text.split())
    reading_time = max(1, word_count // words_per_minute)
    return reading_time


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла от недопустимых символов
    
    Args:
        filename: Исходное имя файла
        
    Returns:
        Очищенное имя файла
    """
    # Заменяем недопустимые символы
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Ограничиваем длину
    filename = filename[:100]
    
    return filename


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Разбивает список на чанки заданного размера
    
    Args:
        lst: Исходный список
        chunk_size: Размер чанка
        
    Returns:
        Список чанков
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_client_ip(request) -> str:
    """
    Получает IP адрес клиента
    
    Args:
        request: HTTP запрос
        
    Returns:
        IP адрес
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_business_hours(current_time: Optional[datetime] = None) -> bool:
    """
    Проверяет, является ли время рабочим
    
    Args:
        current_time: Время для проверки (по умолчанию текущее)
        
    Returns:
        True если рабочее время
    """
    if current_time is None:
        current_time = timezone.now()
    
    # Рабочие дни: понедельник-пятница (0-4)
    if current_time.weekday() >= 5:
        return False
    
    # Рабочие часы: 9:00-18:00
    hour = current_time.hour
    return 9 <= hour < 18


def send_notification_email(
    to_emails: List[str],
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    from_email: Optional[str] = None
) -> bool:
    """
    Отправляет уведомление по email
    
    Args:
        to_emails: Список email получателей
        subject: Тема письма
        template_name: Имя шаблона
        context: Контекст для шаблона
        from_email: Email отправителя
        
    Returns:
        True если отправлено успешно
    """
    try:
        html_content = render_to_string(template_name, context)
        
        send_mail(
            subject=subject,
            message='',  # Текстовая версия (пустая)
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=to_emails,
            html_message=html_content,
            fail_silently=False
        )
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка отправки email: {str(e)}")
        return False


def parse_telegram_entities(text: str, entities: List[Dict]) -> str:
    """
    Парсит Telegram entities и конвертирует в HTML
    
    Args:
        text: Исходный текст
        entities: Список entities от Telegram
        
    Returns:
        HTML текст
    """
    if not entities:
        return text
    
    # Сортируем entities по offset в обратном порядке
    sorted_entities = sorted(entities, key=lambda x: x.get('offset', 0), reverse=True)
    
    result = text
    for entity in sorted_entities:
        entity_type = entity.get('type')
        offset = entity.get('offset', 0)
        length = entity.get('length', 0)
        
        if entity_type == 'bold':
            result = result[:offset] + '<b>' + result[offset:offset+length] + '</b>' + result[offset+length:]
        elif entity_type == 'italic':
            result = result[:offset] + '<i>' + result[offset:offset+length] + '</i>' + result[offset+length:]
        elif entity_type == 'code':
            result = result[:offset] + '<code>' + result[offset:offset+length] + '</code>' + result[offset+length:]
        elif entity_type == 'url':
            url = result[offset:offset+length]
            result = result[:offset] + f'<a href="{url}">{url}</a>' + result[offset+length:]
    
    return result


def mask_sensitive_data(data: str, mask_char: str = '*', show_chars: int = 4) -> str:
    """
    Маскирует чувствительные данные
    
    Args:
        data: Данные для маскировки
        mask_char: Символ маски
        show_chars: Количество символов для показа в начале и конце
        
    Returns:
        Замаскированные данные
    """
    if len(data) <= show_chars * 2:
        return mask_char * len(data)
    
    return data[:show_chars] + mask_char * (len(data) - show_chars * 2) + data[-show_chars:]


def get_user_display_name(user) -> str:
    """
    Получает отображаемое имя пользователя
    
    Args:
        user: Объект пользователя
        
    Returns:
        Отображаемое имя
    """
    if hasattr(user, 'name') and user.name:
        return user.name
    elif hasattr(user, 'first_name') and user.first_name:
        full_name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            full_name += f" {user.last_name}"
        return full_name
    elif hasattr(user, 'username') and user.username:
        return user.username
    elif hasattr(user, 'email') and user.email:
        return user.email.split('@')[0]
    else:
        return f"User {user.id}"


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Валидирует расширение файла
    
    Args:
        filename: Имя файла
        allowed_extensions: Список разрешенных расширений
        
    Returns:
        True если расширение разрешено
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def convert_bytes_to_human_readable(bytes_count: int) -> str:
    """
    Конвертирует байты в читаемый формат
    
    Args:
        bytes_count: Количество байт
        
    Returns:
        Читаемый размер
    """
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} ПБ"


def get_object_or_none(model, **kwargs):
    """
    Получает объект или возвращает None если не найден
    
    Args:
        model: Модель Django
        **kwargs: Параметры фильтрации
        
    Returns:
        Объект или None
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def batch_update_objects(model, updates: List[Dict[str, Any]], batch_size: int = 1000):
    """
    Массовое обновление объектов
    
    Args:
        model: Модель Django
        updates: Список словарей с обновлениями {'id': ..., 'field': value}
        batch_size: Размер батча
    """
    objects_to_update = []
    
    for update_data in updates:
        obj_id = update_data.pop('id')
        try:
            obj = model.objects.get(id=obj_id)
            for field, value in update_data.items():
                setattr(obj, field, value)
            objects_to_update.append(obj)
            
            # Обновляем батчами
            if len(objects_to_update) >= batch_size:
                fields_to_update = list(update_data.keys()) + ['updated_at']
                model.objects.bulk_update(objects_to_update, fields_to_update)
                objects_to_update = []
                
        except model.DoesNotExist:
            continue
    
    # Обновляем оставшиеся объекты
    if objects_to_update:
        fields_to_update = list(updates[0].keys()) + ['updated_at'] if updates else ['updated_at']
        fields_to_update = [f for f in fields_to_update if f != 'id']
        model.objects.bulk_update(objects_to_update, fields_to_update)


def create_deep_link(path: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Создает deep link для Telegram Mini App
    
    Args:
        path: Путь в приложении
        params: Параметры URL
        
    Returns:
        Deep link
    """
    base_url = getattr(settings, 'TELEGRAM_MINI_APP_URL', '')
    if not base_url:
        return path
    
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    
    if params:
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        url += f"?{query_string}"
    
    return url


def generate_qr_code_data(text: str) -> str:
    """
    Генерирует данные для QR кода (base64)
    Требует установки qrcode библиотеки
    
    Args:
        text: Текст для кодирования
        
    Returns:
        Base64 данные изображения
    """
    try:
        import qrcode
        import io
        import base64
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except ImportError:
        return ""  # qrcode не установлен


def get_working_days_count(start_date=None, end_date=None):
    """
    Подсчет рабочих дней в указанном диапазоне
    """
    if not start_date:
        start_date = timezone.now().date()
    if not end_date:
        end_date = start_date + timedelta(days=30)  # По умолчанию смотрим на месяц вперед
    
    # Сначала проверяем в календаре рабочих дней
    calendar_days = WorkingCalendar.objects.filter(
        date__range=(start_date, end_date)
    ).values_list('date', 'is_working_day')
    
    # Преобразуем в словарь для быстрого доступа
    calendar_dict = {day: is_working for day, is_working in calendar_days}
    
    # Счетчик рабочих дней
    working_days = 0
    current = start_date
    
    while current <= end_date:
        # Если дата есть в нашем календаре, используем оттуда
        if current in calendar_dict:
            if calendar_dict[current]:
                working_days += 1
        # Иначе используем стандартную логику (пн-пт)
        elif current.weekday() < 5:  # 0-4 = пн-пт
            working_days += 1
        
        current += timedelta(days=1)
    
    return working_days


def add_working_days(start_date, working_days_to_add):
    """
    Добавляет указанное количество рабочих дней к дате
    
    Args:
        start_date (date): Начальная дата
        working_days_to_add (int): Количество рабочих дней для добавления
        
    Returns:
        date: Дата с учетом добавленных рабочих дней
    """
    if working_days_to_add <= 0:
        return start_date
    
    current = start_date
    days_added = 0
    
    while days_added < working_days_to_add:
        current += timedelta(days=1)
        
        # Проверяем в календаре
        calendar_day = WorkingCalendar.objects.filter(date=current).first()
        if calendar_day:
            if calendar_day.is_working_day:
                days_added += 1
        # Если нет в календаре, проверяем по дням недели
        elif current.weekday() < 5:  # 0-4 = пн-пт
            days_added += 1
    
    return current