import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock
import requests
from apps.flows.models import Flow, FlowStep, UserFlow, Task, Quiz, QuizQuestion, QuizAnswer
from apps.guides.models import Article
from apps.users.models import Role, UserRole
from django.utils import timezone

User = get_user_model()

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
            UserRole.objects.get_or_create(user=user, role=role_obj)
        
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
            'step_type': FlowStep.StepType.ARTICLE
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
    
    article1 = article_factory(title='Article 1', slug='article-1')
    step1 = flow_step_factory(flow, title='Step 1: Article', step_type=FlowStep.StepType.ARTICLE, article=article1, order=1)
    
    step2 = flow_step_factory(flow, title='Step 2: Task', step_type=FlowStep.StepType.TASK, order=2)
    task = Task.objects.create(flow_step=step2, title='Task 1', description='Do the task', code_word='secret')
    
    step3 = flow_step_factory(flow, title='Step 3: Quiz', step_type=FlowStep.StepType.QUIZ, order=3)
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