"""
Скрипт установки и настройки приложения.
Запускает все необходимые команды инициализации, включая генерацию тестовых токенов.
"""

import os
import logging
import subprocess
from django.core.management import call_command

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def setup_application():
    """
    Основная функция настройки приложения.
    Выполняет все необходимые шаги для инициализации системы.
    """
    try:
        # Шаг 1: Применение миграций
        logger.info("Применение миграций базы данных...")
        call_command('migrate')
        logger.info("[SUCCESS] Миграции применены успешно")
        
        # Шаг 2: Сбор статических файлов
        logger.info("Сбор статических файлов...")
        call_command('collectstatic', '--noinput')
        logger.info("[SUCCESS] Статические файлы собраны")
        
        # Шаг 3: Настройка системы (роли, пользователи, задачи Celery)
        logger.info("Настройка системы (роли, суперпользователь, Celery Beat)...")
        call_command('setup_system')
        logger.info("[SUCCESS] Система настроена успешно")
        
        # Шаг 4: Загрузка демонстрационных данных
        logger.info("Загрузка демонстрационных данных...")
        call_command('load_demo_data')
        logger.info("[SUCCESS] Демонстрационные данные загружены успешно")
        
        # Шаг 5: Генерация тестовых JWT-токенов
        logger.info("Генерация тестовых JWT-токенов...")
        call_command('generate_tokens')
        logger.info("[SUCCESS] Тестовые токены сгенерированы успешно")
        
        logger.info("Инициализация завершена.")
        
    except Exception as e:
        logger.error(f"Ошибка при настройке приложения: {str(e)}")
        raise

if __name__ == "__main__":
    # Запуск процесса настройки
    setup_application()
    
    # Запуск веб-сервера
    logger.info("Запуск веб-сервера...")
    subprocess.call(["python", "manage.py", "runserver", "0.0.0.0:8000"])