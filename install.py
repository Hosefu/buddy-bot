#!/usr/bin/env python
"""
Упрощенный скрипт установки системы онбординга

Использует Django management команды для безопасной инициализации
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """Настройка окружения Python"""
    # Устанавливаем переменную окружения для настроек Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onboarding.settings')
    
    # Добавляем текущую директорию в Python path
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))


def run_django_command(command, description):
    """Запуск Django management команды через subprocess"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py'] + command,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        print(f"✅ {description} - успешно завершено")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def create_directories():
    """Создание необходимых директорий"""
    print("\n📁 Создание директорий...")
    
    directories = [
        'logs',
        'media', 
        'staticfiles',
        'static',
        'apps/common/management',
        'apps/common/management/commands',
    ]
    
    base_dir = Path(__file__).resolve().parent
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана/проверена директория: {dir_name}")
    
    return True


def create_management_command():
    """Создание Django management команды если её нет"""
    management_dir = Path(__file__).resolve().parent / 'apps/common/management'
    commands_dir = management_dir / 'commands'
    
    # Создаем __init__.py файлы
    for init_file in [management_dir / '__init__.py', commands_dir / '__init__.py']:
        if not init_file.exists():
            init_file.touch()
            print(f"✅ Создан файл: {init_file}")


def check_environment():
    """Проверка переменных окружения"""
    print("\n🔍 Проверка переменных окружения...")
    
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️  Отсутствуют переменные: {', '.join(missing_vars)}")
        print("ℹ️  Будут использованы значения по умолчанию")
    else:
        print("✅ Все обязательные переменные установлены")
    
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        print("⚠️  TELEGRAM_BOT_TOKEN не установлен")
    else:
        print("✅ TELEGRAM_BOT_TOKEN установлен")
    
    return True


def main():
    """Основная функция установки"""
    print(f"\n{'='*60}")
    print("🚀 УСТАНОВКА СИСТЕМЫ ОНБОРДИНГА")
    print(f"{'='*60}")
    
    # Настройка окружения
    setup_environment()
    
    # Шаги установки
    steps = [
        (check_environment, "Проверка окружения"),
        (create_directories, "Создание директорий"),
        (create_management_command, "Создание Django команд"),
        (lambda: run_django_command(['migrate'], "Применение миграций"), None),
        (lambda: run_django_command(['collectstatic', '--noinput'], "Сбор статических файлов"), None),
        (lambda: run_django_command(['setup_system'], "Настройка системы"), None),
        (lambda: run_django_command(['load_demo_data'], "Загрузка демо-данных"), None),
        (lambda: run_django_command(['generate_tokens'], "Генерация токенов"), None),
    ]
    
    failed_steps = []
    
    for step_func, description in steps:
        if description:
            print(f"\n🔧 {description}")
            
        try:
            if not step_func():
                failed_steps.append(description or "Неизвестный шаг")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            failed_steps.append(description or "Неизвестный шаг")
    
    # Результат
    if failed_steps:
        print(f"\n⚠️  Установка завершена с ошибками: {', '.join(failed_steps)}")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print("🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*60}")
        print("\n🔗 Полезные ссылки:")
        print("   • API: http://localhost:8000/api/")
        print("   • Админка: http://localhost:8000/admin/")
        print("   • Документация: http://localhost:8000/api/docs/")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()