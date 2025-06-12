#!/usr/bin/env python
"""
Единая система установки и управления проектом онбординга.
Этот файл - основная точка входа для всех операций установки и настройки.

Использование:
    python setup.py install              # Полная установка системы
    python setup.py migrate              # Только миграции БД
    python setup.py static               # Сборка статических файлов
    python setup.py createsuperuser      # Создание администратора
    python setup.py demo                 # Загрузка демо-данных
    python setup.py check                # Проверка системы
    python setup.py setup-webhook        # Настройка вебхука Telegram
    python setup.py --help               # Справка по командам

При запуске через Docker:
    docker-compose exec web python setup.py [команда]
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='\033[1;34m[%(levelname)s]\033[0m %(message)s'
)
logger = logging.getLogger("setup")

# Цвета для логов
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Конфигурация системы
CONFIG = {
    'django_app': 'onboarding',
    'settings_module': 'onboarding.settings',
    'required_dirs': [
        'logs',
        'media',
        'staticfiles',
        'apps/common/management/commands',
    ],
    'management_commands': [
        'setup_system',
        'load_demo_data',
        'generate_tokens',
    ]
}


def setup_environment():
    """Настройка окружения Python для работы с Django"""
    # Устанавливаем переменную окружения для настроек Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', CONFIG['settings_module'])
    
    # Добавляем текущую директорию в Python path
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))


def run_django_command(command, description=None, capture_output=True):
    """
    Запуск Django management команды
    
    Args:
        command (list): Список аргументов команды
        description (str, optional): Описание команды для вывода
        capture_output (bool): Захватывать ли вывод
    
    Returns:
        bool: Успешность выполнения
    """
    if description:
        logger.info(f"{BOLD}{description}{RESET}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py'] + command,
            check=True,
            capture_output=capture_output,
            text=True
        )
        
        if capture_output:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
                
        if description:
            logger.info(f"{GREEN}✓ {description} - успешно{RESET}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"{RED}✗ Ошибка: {e}{RESET}")
        if capture_output:
            if e.stdout:
                print(f"{YELLOW}STDOUT:{RESET}", e.stdout)
            if e.stderr:
                print(f"{RED}STDERR:{RESET}", e.stderr)
        return False
    except Exception as e:
        logger.error(f"{RED}✗ Неожиданная ошибка: {e}{RESET}")
        return False


def create_required_directories():
    """Создание необходимых директорий для работы приложения"""
    logger.info(f"{BOLD}Создание необходимых директорий{RESET}")
    
    base_dir = Path(__file__).resolve().parent
    
    for dir_path in CONFIG['required_dirs']:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"{GREEN}✓ Создана/проверена директория: {dir_path}{RESET}")
    
    # Создаем __init__.py файлы для пакетов
    for init_path in [
        'apps/__init__.py',
        'apps/common/__init__.py',
        'apps/common/management/__init__.py',
        'apps/common/management/commands/__init__.py'
    ]:
        init_file = base_dir / init_path
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.touch()
            logger.info(f"{GREEN}✓ Создан файл: {init_path}{RESET}")
    
    return True


def check_environment():
    """Проверка переменных окружения и требований системы"""
    logger.info(f"{BOLD}Проверка окружения{RESET}")
    
    # Проверка переменных окружения
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"{YELLOW}⚠️ Отсутствуют переменные: {', '.join(missing_vars)}{RESET}")
        logger.info("ℹ️ Будут использованы значения по умолчанию")
    else:
        logger.info(f"{GREEN}✓ Все обязательные переменные установлены{RESET}")
    
    # Проверка Telegram токена
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        logger.warning(f"{YELLOW}⚠️ TELEGRAM_BOT_TOKEN не установлен{RESET}")
    else:
        logger.info(f"{GREEN}✓ TELEGRAM_BOT_TOKEN установлен{RESET}")
    
    # Проверка наличия зависимостей Python
    try:
        import django
        logger.info(f"{GREEN}✓ Django {django.__version__} установлен{RESET}")
    except ImportError:
        logger.error(f"{RED}✗ Django не установлен. Выполните: pip install -r requirements.txt{RESET}")
        return False
    
    try:
        import celery
        logger.info(f"{GREEN}✓ Celery {celery.__version__} установлен{RESET}")
    except ImportError:
        logger.warning(f"{YELLOW}⚠️ Celery не установлен. Некоторые функции могут быть недоступны{RESET}")
    
    # Проверка доступа к базе данных
    if os.environ.get('DB_HOST'):
        try:
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '5432')
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((db_host, int(db_port)))
            s.close()
            if result == 0:
                logger.info(f"{GREEN}✓ База данных доступна: {db_host}:{db_port}{RESET}")
            else:
                logger.warning(f"{YELLOW}⚠️ База данных недоступна: {db_host}:{db_port}{RESET}")
        except Exception as e:
            logger.warning(f"{YELLOW}⚠️ Не удалось проверить базу данных: {e}{RESET}")
    
    return True


def migrate_database():
    """Применение миграций базы данных"""
    return run_django_command(['migrate', '--noinput'], "Применение миграций базы данных")


def collect_static():
    """Сбор статических файлов"""
    return run_django_command(['collectstatic', '--noinput', '--clear'], "Сбор статических файлов")


def setup_system():
    """Настройка системы: роли, суперпользователь, Celery Beat"""
    return run_django_command(['setup_system'], "Настройка системы (роли, суперпользователь, Celery Beat)")


def load_demo_data():
    """Загрузка демонстрационных данных"""
    return run_django_command(['load_demo_data'], "Загрузка демонстрационных данных")


def generate_tokens():
    """Генерация тестовых токенов для API"""
    return run_django_command(['generate_tokens'], "Генерация тестовых токенов")


def create_superuser():
    """Интерактивное создание суперпользователя"""
    return run_django_command(['createsuperuser'], "Создание суперпользователя", capture_output=False)


def setup_telegram_webhook():
    """Настройка вебхука для Telegram бота"""
    logger.info(f"{BOLD}Настройка вебхука Telegram{RESET}")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    webhook_url = os.environ.get('TELEGRAM_WEBHOOK_URL')
    
    if not token:
        logger.error(f"{RED}✗ Не установлен TELEGRAM_BOT_TOKEN{RESET}")
        return False
    
    if not webhook_url:
        logger.error(f"{RED}✗ Не установлен TELEGRAM_WEBHOOK_URL{RESET}")
        return False
    
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        response = requests.post(
            url,
            json={'url': webhook_url}
        )
        response_data = response.json()
        
        if response_data.get('ok'):
            logger.info(f"{GREEN}✓ Вебхук успешно установлен: {webhook_url}{RESET}")
            return True
        else:
            logger.error(f"{RED}✗ Ошибка установки вебхука: {response_data.get('description')}{RESET}")
            return False
    except Exception as e:
        logger.error(f"{RED}✗ Ошибка при настройке вебхука: {e}{RESET}")
        return False


def check_system():
    """Проверка работоспособности системы"""
    logger.info(f"{BOLD}Проверка системы{RESET}")
    
    # Проверка Django
    try:
        result = run_django_command(['check'], "Проверка Django")
        if not result:
            return False
    except Exception as e:
        logger.error(f"{RED}✗ Ошибка проверки Django: {e}{RESET}")
        return False
    
    # Проверка базы данных
    try:
        import django
        django.setup()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row[0] == 1:
                logger.info(f"{GREEN}✓ Соединение с базой данных успешно{RESET}")
            else:
                logger.error(f"{RED}✗ Ошибка соединения с базой данных{RESET}")
                return False
    except Exception as e:
        logger.error(f"{RED}✗ Ошибка проверки базы данных: {e}{RESET}")
        return False
    
    # Проверка Redis (если используется)
    if 'REDIS_URL' in os.environ:
        try:
            import redis
            redis_url = os.environ.get('REDIS_URL')
            r = redis.from_url(redis_url)
            r.ping()
            logger.info(f"{GREEN}✓ Соединение с Redis успешно{RESET}")
        except ImportError:
            logger.warning(f"{YELLOW}⚠️ Библиотека redis не установлена{RESET}")
        except Exception as e:
            logger.warning(f"{YELLOW}⚠️ Ошибка соединения с Redis: {e}{RESET}")
    
    # Проверка версий компонентов
    try:
        import platform
        import django
        
        logger.info(f"{BLUE}Информация о системе:{RESET}")
        logger.info(f"  • Python: {platform.python_version()}")
        logger.info(f"  • Django: {django.__version__}")
        logger.info(f"  • OS: {platform.system()} {platform.release()}")
        
        try:
            import celery
            logger.info(f"  • Celery: {celery.__version__}")
        except ImportError:
            pass
        
        try:
            import rest_framework
            logger.info(f"  • Django REST Framework: {rest_framework.VERSION}")
        except ImportError:
            pass
    except Exception as e:
        logger.warning(f"{YELLOW}⚠️ Ошибка при получении информации о версиях: {e}{RESET}")
    
    logger.info(f"{GREEN}✓ Проверка системы завершена успешно{RESET}")
    return True


def full_install():
    """Полная установка системы"""
    logger.info(f"\n{BOLD}{'='*60}\n🚀 ПОЛНАЯ УСТАНОВКА СИСТЕМЫ ОНБОРДИНГА\n{'='*60}{RESET}\n")
    
    steps = [
        (check_environment, "Проверка окружения"),
        (create_required_directories, "Создание директорий"),
        (migrate_database, "Применение миграций"),
        (collect_static, "Сбор статических файлов"),
        (setup_system, "Настройка системы"),
        (load_demo_data, "Загрузка демо-данных"),
        (generate_tokens, "Генерация токенов API"),
    ]
    
    failed_steps = []
    
    for step_func, description in steps:
        logger.info(f"\n{BOLD}ЭТАП: {description}{RESET}")
        try:
            if not step_func():
                failed_steps.append(description)
        except Exception as e:
            logger.error(f"{RED}✗ Критическая ошибка: {e}{RESET}")
            failed_steps.append(description)
    
    # Результат
    print("\n")
    if failed_steps:
        logger.warning(f"\n{YELLOW}⚠️  Установка завершена с ошибками: {', '.join(failed_steps)}{RESET}")
        sys.exit(1)
    else:
        logger.info(f"\n{BOLD}{'='*60}\n{GREEN}🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!{RESET}\n{BOLD}{'='*60}{RESET}")
        logger.info(f"\n{BLUE}🔗 Полезные ссылки:{RESET}")
        logger.info(f"   • API: http://localhost:8000/api/")
        logger.info(f"   • Админка: http://localhost:8000/admin/")
        logger.info(f"   • Документация: http://localhost:8000/api/docs/")
        logger.info(f"{BOLD}{'='*60}{RESET}")


def display_help():
    """Выводит справку по использованию"""
    help_text = f"""
{BOLD}Система установки и управления проектом онбординга{RESET}

{BLUE}Использование:{RESET}
  python setup.py [команда]

{BLUE}Доступные команды:{RESET}
  install             Полная установка системы
  migrate             Только миграции БД
  static              Сборка статических файлов
  createsuperuser     Создание администратора
  demo                Загрузка демо-данных
  check               Проверка системы
  setup-webhook       Настройка вебхука Telegram
  help                Эта справка

{BLUE}Примеры:{RESET}
  python setup.py install
  docker-compose exec web python setup.py check
"""
    print(help_text)


def main():
    """Основная функция"""
    setup_environment()
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description='Система установки и управления проектом онбординга',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default='help',
                        help='Команда для выполнения')
    
    args = parser.parse_args()
    
    # Выполнение соответствующей команды
    command_map = {
        'install': full_install,
        'migrate': migrate_database,
        'static': collect_static,
        'createsuperuser': create_superuser,
        'demo': load_demo_data,
        'check': check_system,
        'setup-webhook': setup_telegram_webhook,
        'help': display_help,
    }
    
    if args.command in command_map:
        command_map[args.command]()
    else:
        logger.error(f"{RED}Неизвестная команда: {args.command}{RESET}")
        display_help()
        sys.exit(1)


if __name__ == '__main__':
    main()