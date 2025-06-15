import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock
import requests
from apps.flows.models import Flow, FlowStep, UserFlow, Task, Quiz, QuizQuestion, QuizAnswer
from apps.guides.models import Article
from apps.users.models import Role, UserRole
from django.utils import timezone
try:
    # Эта фикстура будет найдена pytest автоматически
    from .test_common_utils import setup_calendar
except ImportError:
    pass
import json
import pytest_html

User = get_user_model()

# --- Fixtures and hooks for HTML reporting ---

@pytest.fixture
def report_data():
    """Фикстура для сбора данных для отчета."""
    return []

def pytest_html_report_title(report):
    """Устанавливаем кастомный заголовок для HTML отчета."""
    report.title = "Отчет о тестировании Buddy Bot API"

def pytest_configure(config):
    """Добавляем метаданные в отчет."""
    # Проверяем, что html отчет создается
    if hasattr(config, 'option') and config.getoption('htmlpath'):
        # Для pytest-metadata >= 2.0.0
        if hasattr(config, 'stash'):
            from pytest_metadata.plugin import metadata_key
            # Убедимся, что ключ метаданных существует
            if metadata_key not in config.stash:
                config.stash[metadata_key] = {}
            
            config.stash[metadata_key]['Project'] = 'Buddy Bot'
            config.stash[metadata_key]['Tester'] = 'Gemini'
            
            # Удаляем ненужные метаданные
            existing_metadata = config.stash[metadata_key]
            for key in ['Packages', 'Plugins', 'Python']:
                if key in existing_metadata:
                    del existing_metadata[key]
        
        # Для старых версий pytest-metadata < 2.0.0
        elif hasattr(config, '_metadata'):
             config._metadata['Project'] = 'Buddy Bot'
             config._metadata['Tester'] = 'Gemini'
             for key in ['Packages', 'Plugins', 'Python']:
                 if key in config._metadata:
                    del config._metadata[key]

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для добавления дополнительной информации в HTML отчет.
    Собирает данные из фикстуры 'report_data' и форматирует их.
    """
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extras', [])
    if report.when == 'call':
        # Проверяем, есть ли у теста фикстура report_data
        if 'report_data' in item.fixturenames:
            report_data = item.funcargs['report_data']
            if report_data:
                # Генерируем HTML-контент для каждого шага
                html_content = ""
                for i, entry in enumerate(report_data):
                    # Безопасно получаем данные, обрабатываем None
                    request_body = entry.get('request_body')
                    response_body = entry.get('response_body')

                    request_dump = json.dumps(request_body, indent=2, ensure_ascii=False) if request_body is not None else "No data"
                    response_dump = json.dumps(response_body, indent=2, ensure_ascii=False) if response_body is not None else "No data"
                    
                    # Формируем HTML блока
                    html_content += f"""
                    <div class="test-step">
                        <h3>Шаг {i+1}: {entry.get('name', 'N/A')}</h3>
                        <p><strong>URL:</strong> {entry.get('url', 'N/A')}</p>
                        <p><strong>Метод:</strong> {entry.get('method', 'N/A')}</p>
                        <p><strong>Статус:</strong> <span class="status-code status-{entry.get('status_code', 'unknown')}">{entry.get('status_code', 'N/A')}</span></p>
                        <h4>Request:</h4>
                        <pre><code>{request_dump}</code></pre>
                        <h4>Response:</h4>
                        <pre><code>{response_dump}</code></pre>
                    </div>
                    """
                # Добавляем стили для лучшего отображения
                styles = """
                <style>
                    .report-box { border: 1px solid #ddd; padding: 15px; margin-top: 20px; border-radius: 5px; background-color: #f9f9f9; }
                    .test-step { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
                    .test-step:last-child { border-bottom: none; }
                    .test-step h3 { color: #333; }
                    .test-step h4 { color: #555; margin-top: 10px; }
                    .status-code { font-weight: bold; padding: 2px 6px; border-radius: 3px; color: white; }
                    .status-200, .status-201, .status-204 { background-color: #28a745; }
                    .status-400, .status-401, .status-403, .status-404, .status-500 { background-color: #dc3545; }
                    .status-unknown { background-color: #ffc107; color: black; }
                    pre { background-color: #eee; padding: 10px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }
                </style>
                """
                # Оборачиваем все в один блок
                final_html = f"{styles}<div class='report-box'><h2>Детали выполнения теста</h2>{html_content}</div>"
                extra.append(pytest_html.extras.html(final_html))
        report.extras = extra

# --- Standard Fixtures ---

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Настройка БД для тестов: очистка и создание ролей."""
    with django_db_blocker.unblock():
        # Очищаем роли перед созданием, чтобы избежать конфликтов
        Role.objects.all().delete()
        for role_name, role_display in Role.RoleChoices.choices:
            Role.objects.get_or_create(name=role_name, defaults={'display_name': role_display})

@pytest.fixture
def api_client():
    """Фикстура для DRF API клиента."""
    return APIClient()

@pytest.fixture
def user_factory(db):
    """Фабрика для создания пользователей с ролями."""
    def create_user(role=None, **kwargs):
        telegram_id = kwargs.pop('telegram_id', f"test_user_{User.objects.count()}_{timezone.now().timestamp()}")
        name = kwargs.pop('name', 'Test User')
        
        # Создаем пользователя. Сигнал должен автоматически назначить ему роль 'user'.
        user = User.objects.create_user(telegram_id=telegram_id, name=name, **kwargs)
        
        # Если нужна дополнительная роль (buddy, moderator), назначаем ее.
        if role and role != Role.RoleChoices.USER:
            role_obj = Role.objects.get(name=role)
            user.roles.add(role_obj)
        
        # Для удобства доступа в тестах
        user.role_name = role or Role.RoleChoices.USER
        
        return user
    return create_user

@pytest.fixture
def user(user_factory):
    """Обычный пользователь."""
    return user_factory(telegram_id='100', name='Test User')

@pytest.fixture
def another_user(user_factory):
    """Еще один обычный пользователь."""
    return user_factory(telegram_id='200', name='Another User')

@pytest.fixture
def buddy_user(user_factory):
    """Пользователь с правами buddy."""
    return user_factory(role=Role.RoleChoices.BUDDY, telegram_id='300', name='Buddy User')

@pytest.fixture
def admin_user(user_factory):
    """Пользователь с правами модератора."""
    return user_factory(role=Role.RoleChoices.MODERATOR, telegram_id='400', name='Admin User', is_staff=True)

@pytest.fixture
def flow_factory(db):
    """Фабрика для создания потоков."""
    def create_flow(**kwargs):
        defaults = {
            'title': 'Test Flow',
            'description': 'A test flow'
        }
        defaults.update(kwargs)
        return Flow.objects.create(**defaults)
    return create_flow

@pytest.fixture
def article_factory(db, user_factory):
    """Фабрика для создания статей."""
    def create_article(**kwargs):
        defaults = {
            'title': 'Test Article',
            'content': 'Some content here'
        }
        if 'author' not in kwargs:
            defaults['author'] = user_factory()
        
        defaults.update(kwargs)

        # Ensure slug is unique if not provided
        if 'slug' not in defaults:
            base_slug = defaults['title'].lower().replace(' ', '-')
            slug = base_slug
            i = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            defaults['slug'] = slug

        # По умолчанию делаем статью опубликованной для тестов API
        if 'is_published' not in defaults:
            defaults['is_published'] = True
        if defaults['is_published'] and 'published_at' not in defaults:
            defaults['published_at'] = timezone.now()
            
        return Article.objects.create(**defaults)
    return create_article

@pytest.fixture
def flow_step_factory(db):
    """Фабрика для создания шагов потока."""
    def create_step(flow, **kwargs):
        defaults = {
            'title': 'Test Step',
            'order': flow.get_next_step_order(),
        }
        defaults.update(kwargs)
        return FlowStep.objects.create(flow=flow, **defaults)
    return create_step

@pytest.fixture
def user_flow_factory(db):
    """Фабрика для назначения потока пользователю."""
    def create_user_flow(user, flow, **kwargs):
        return UserFlow.objects.create(user=user, flow=flow, **kwargs)
    return create_user_flow

@pytest.fixture
def simple_flow(flow_factory):
    """Простой поток с одним шагом."""
    return flow_factory(title='Simple Flow', description='A simple flow for testing.')

@pytest.fixture
def flow_with_steps(flow_factory, flow_step_factory, article_factory):
    """Поток с несколькими шагами разного типа."""
    flow = flow_factory(title='Complex Flow', description='Flow with multiple steps')
    
    step1 = flow_step_factory(flow, title='Step 1: Article', order=1)
    article1 = article_factory(title='Article 1', slug='article-1', flow_step=step1)

    step2 = flow_step_factory(flow, title='Step 2: Task', order=2)
    task = Task.objects.create(flow_step=step2, title='Task 1', description='Do the task', code_word='secret')

    step3 = flow_step_factory(flow, title='Step 3: Quiz', order=3)
    quiz = Quiz.objects.create(flow_step=step3, title='Quiz 1')
    question = QuizQuestion.objects.create(quiz=quiz, question='What is 1+1?', order=1)
    QuizAnswer.objects.create(question=question, answer_text='2', is_correct=True, order=1)
    QuizAnswer.objects.create(question=question, answer_text='3', is_correct=False, order=2)
    
    return flow

@pytest.fixture(autouse=True)
def mock_telegram_request(mocker):
    """
    Мокает запросы к API Telegram во всех тестах.
    Это предотвращает реальные HTTP-запросы во время тестов.
    """
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {'ok': True, 'result': {}}
    mock_response.text = '{"ok": true, "result": {}}'

    # Мокаем метод post в модуле, где он используется (в задачах Celery)
    return mocker.patch('apps.users.tasks.requests.post', return_value=mock_response) 