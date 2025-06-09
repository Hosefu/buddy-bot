# Структура Django проекта для системы онбординга

```
telegram_onboarding/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
└── onboarding/
    ├── __init__.py
    ├── settings/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── development.py
    │   ├── production.py
    │   └── testing.py
    ├── urls.py
    ├── wsgi.py
    ├── asgi.py
    └── celery.py
├── apps/
    ├── __init__.py
    ├── users/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── permissions.py
    │   ├── utils.py
    │   ├── urls.py
    │   ├── managers.py
    │   └── migrations/
    │       └── __init__.py
    ├── flows/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── permissions.py
    │   ├── utils.py
    │   ├── urls.py
    │   ├── managers.py
    │   ├── services.py
    │   └── migrations/
    │       └── __init__.py
    ├── guides/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── permissions.py
    │   ├── utils.py
    │   ├── urls.py
    │   ├── managers.py
    │   └── migrations/
    │       └── __init__.py
    └── common/
        ├── __init__.py
        ├── models.py
        ├── permissions.py
        ├── mixins.py
        ├── utils.py
        ├── exceptions.py
        └── validators.py
```
