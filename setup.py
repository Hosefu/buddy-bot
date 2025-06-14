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
    python setup.py test                 # Запуск тестов
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
        'reports', # Директория для отчетов о тестах
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
            text=True,
            encoding='utf-8'
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


def run_tests():
    """Запуск тестов с использованием pytest"""
    logger.info(f"{BOLD}Запуск тестов...{RESET}")
    try:
        # Вызываем pytest как модуль, чтобы использовать правильный python-интерпретатор
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--junitxml=reports/pytest-report.xml'],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        # Печатаем вывод pytest, чтобы видеть прогресс и результаты
        if result.stdout:
            print(result.stdout)
        logger.info(f"{GREEN}✓ Все тесты пройдены успешно!{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"{RED}✗ Некоторые тесты не пройдены. Смотрите отчет выше.{RESET}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(f"{RED}STDERR:{RESET}", e.stderr)
        return False
    except FileNotFoundError:
        logger.error(f"{RED}✗ Команда pytest не найдена. Убедитесь, что pytest установлен (pip install pytest).{RESET}")
        return False
    except Exception as e:
        logger.error(f"{RED}✗ Не удалось запустить тесты: {e}{RESET}")
        return False


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
        
        if response.ok and response_data.get('ok'):
            logger.info(f"{GREEN}✓ Вебхук успешно установлен: {response_data.get('description')}{RESET}")
            return True
        else:
            logger.error(f"{RED}✗ Ошибка установки вебхука: {response_data.get('description')}{RESET}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"{RED}✗ Ошибка сети при установке вебхука: {e}{RESET}")
        return False


def check_system():
    """
    Комплексная проверка системы:
    - Проверка окружения
    - Проверка миграций
    - Проверка статических файлов
    """
    logger.info(f"\n{BOLD}{'='*60}\n🔬 ЗАПУСК ПРОВЕРКИ СИСТЕМЫ\n{'='*60}{RESET}\n")
    
    failed_checks = []
    
    # 1. Проверка окружения
    logger.info(f"{BLUE}--- Проверка окружения ---{RESET}")
    if not check_environment():
        failed_checks.append("Проверка окружения")
    
    # 2. Проверка миграций
    logger.info(f"\n{BLUE}--- Проверка статуса миграций ---{RESET}")
    try:
        # Запускаем showmigrations и проверяем, что все применены
        result = subprocess.run(
            [sys.executable, 'manage.py', 'showmigrations', '--plan'],
            capture_output=True, text=True, check=True
        )
        if '(no migrations)' in result.stdout or '[X]' in result.stdout:
            logger.info(f"{GREEN}✓ Все миграции применены{RESET}")
        else:
            logger.warning(f"{YELLOW}⚠️ Есть непримененные миграции{RESET}")
            failed_checks.append("Миграции")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"{RED}✗ Не удалось проверить миграции: {e.stderr}{RESET}")
        failed_checks.append("Миграции")
        
    # 3. Проверка статических файлов
    logger.info(f"\n{BLUE}--- Проверка статических файлов ---{RESET}")
    static_dir = Path(CONFIG.get('django_app', 'onboarding')) / 'static'
    if not static_dir.exists() or not any(static_dir.iterdir()):
        logger.warning(f"{YELLOW}⚠️ Директория со статикой пуста. Запустите 'collectstatic'{RESET}")
    else:
        logger.info(f"{GREEN}✓ Статические файлы на месте{RESET}")

    # Итог
    if not failed_checks:
        logger.info(f"\n{GREEN}{BOLD}✅ Проверка системы завершена успешно!{RESET}")
        return True
    else:
        logger.error(f"\n{RED}{BOLD}❌ Проверка системы выявила проблемы: {', '.join(failed_checks)}{RESET}")
        return False


def full_install():
    """Полная установка системы"""
    logger.info(f"\n{BOLD}{'='*60}\n🚀 ПОЛНАЯ УСТАНОВКА СИСТЕМЫ ОНБОРДИНГА\n{'='*60}{RESET}\n")
    
    steps = [
        (check_environment, "Проверка окружения"),
        (create_required_directories, "Создание директорий"),
        (migrate_database, "Применение миграций"),
        (setup_system, "Настройка системы"),
        (run_tests, "Запуск тестов"),
        (collect_static, "Сбор статических файлов"),
        (load_demo_data, "Загрузка демо-данных"),
        (generate_tokens, "Генерация токенов API"),
    ]
    
    failed_steps = []
    
    for step_func, description in steps:
        logger.info(f"\n{BOLD}ЭТАП: {description}{RESET}")
        try:
            if not step_func():
                failed_steps.append(description)
                logger.error(f"{RED}✗ Этап '{description}' завершился с ошибкой.{RESET}")
        except Exception as e:
            failed_steps.append(description)
            logger.error(f"{RED}✗ Критическая ошибка на этапе '{description}': {e}{RESET}")

    if not failed_steps:
        logger.info(f"\n{GREEN}{BOLD}{'='*60}\n✅ СИСТЕМА УСПЕШНО УСТАНОВЛЕНА И НАСТРОЕНА\n{'='*60}{RESET}")
        return True
    else:
        logger.warning(f"\n{YELLOW}{BOLD}{'='*60}\n⚠️  Установка завершена с ошибками: {', '.join(failed_steps)}\n{'='*60}{RESET}")
        return False


def display_help():
    """Отображение справки по командам"""
    help_text = f"""
{BOLD}Система управления проектом онбординга{RESET}

{BOLD}Использование:{RESET}
  python setup.py [команда]

{BOLD}Доступные команды:{RESET}
  install           Полная установка и настройка системы
  migrate           Применение миграций базы данных
  static            Сборка статических файлов
  createsuperuser   Интерактивное создание администратора
  demo              Загрузка демонстрационных данных
  check             Комплексная проверка системы
  setup-webhook     Настройка вебхука Telegram
  test              Запуск тестов
  help              Эта справка
"""
    print(help_text)


def main():
    """Основная функция-диспетчер"""
    # --- Настройка окружения ---
    setup_environment()
    
    # --- Парсинг аргументов командной строки ---
    parser = argparse.ArgumentParser(
        description='Система установки и управления проектом онбординга',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default='help',
                        help='Команда для выполнения')
    
    args = parser.parse_args()
    
    # --- Выполнение соответствующей команды ---
    command_map = {
        'install': full_install,
        'migrate': migrate_database,
        'static': collect_static,
        'createsuperuser': create_superuser,
        'demo': load_demo_data,
        'check': check_system,
        'setup-webhook': setup_telegram_webhook,
        'test': run_tests,
        'help': display_help,
    }
    
    if args.command in command_map:
        if not command_map[args.command]():
            # Если команда завершилась с ошибкой, выходим с ненулевым кодом
            sys.exit(1)
    else:
        logger.error(f"{RED}Неизвестная команда: {args.command}{RESET}")
        display_help()
        sys.exit(1)

if __name__ == '__main__':
    main()