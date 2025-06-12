# Makefile для удобного управления проектом онбординга
# Автор: AI Claude 3.7 Sonnet

# Переменные
COMPOSE = docker-compose
PYTHON = python
MANAGE = $(PYTHON) manage.py

# Общие команды
.PHONY: help
help: ## Показать эту справку
	@echo "Управление проектом онбординга"
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Полная установка системы
	$(PYTHON) setup.py install

.PHONY: run
run: ## Запуск системы в режиме разработки
	$(COMPOSE) up

.PHONY: run-d
run-d: ## Запуск системы в фоновом режиме
	$(COMPOSE) up -d

.PHONY: stop
stop: ## Остановка системы
	$(COMPOSE) stop

.PHONY: down
down: ## Полная остановка и удаление контейнеров
	$(COMPOSE) down

.PHONY: build
build: ## Сборка образов
	$(COMPOSE) build

.PHONY: restart
restart: down run-d ## Перезапуск системы

.PHONY: clean
clean: ## Очистка временных файлов
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.orig" -delete

# Django команды
.PHONY: migrate
migrate: ## Применить миграции
	$(MANAGE) migrate

.PHONY: makemigrations
makemigrations: ## Создать миграции
	$(MANAGE) makemigrations

.PHONY: shell
shell: ## Django shell
	$(MANAGE) shell

.PHONY: superuser
superuser: ## Создать суперпользователя
	$(MANAGE) createsuperuser

.PHONY: collectstatic
collectstatic: ## Собрать статические файлы
	$(MANAGE) collectstatic --noinput

.PHONY: check
check: ## Проверка системы
	$(PYTHON) setup.py check

# Docker команды
.PHONY: logs
logs: ## Показать логи
	$(COMPOSE) logs -f

.PHONY: logs-web
logs-web: ## Показать логи веб-сервера
	$(COMPOSE) logs -f web

.PHONY: logs-celery
logs-celery: ## Показать логи Celery
	$(COMPOSE) logs -f celery-worker

.PHONY: logs-beat
logs-beat: ## Показать логи Celery Beat
	$(COMPOSE) logs -f celery-beat

.PHONY: ps
ps: ## Статус контейнеров
	$(COMPOSE) ps

.PHONY: exec-web
exec-web: ## Bash в веб-контейнере
	$(COMPOSE) exec web bash

.PHONY: exec-db
exec-db: ## Psql в контейнере базы данных
	$(COMPOSE) exec db psql -U postgres -d onboarding

# Установка через Docker
.PHONY: docker-install
docker-install: ## Установка через Docker
	$(COMPOSE) exec web $(PYTHON) setup.py install

.PHONY: docker-migrate
docker-migrate: ## Миграции через Docker
	$(COMPOSE) exec web $(MANAGE) migrate

.PHONY: docker-superuser
docker-superuser: ## Создание суперпользователя через Docker
	$(COMPOSE) exec web $(MANAGE) createsuperuser

.PHONY: docker-static
docker-static: ## Сбор статики через Docker
	$(COMPOSE) exec web $(MANAGE) collectstatic --noinput

.PHONY: docker-check
docker-check: ## Проверка системы через Docker
	$(COMPOSE) exec web $(PYTHON) setup.py check

# Разработка
.PHONY: lint
lint: ## Проверка кода
	flake8 .

.PHONY: test
test: ## Запуск тестов
	$(MANAGE) test

.PHONY: coverage
coverage: ## Тесты с покрытием
	coverage run --source='.' $(MANAGE) test
	coverage report

# Документация
.PHONY: docs
docs: ## Генерация документации
	cd docs && make html

# Продакшн команды
.PHONY: prod-up
prod-up: ## Запуск в режиме продакшн
	$(COMPOSE) --profile production up -d

.PHONY: prod-deploy
prod-deploy: ## Деплой в продакшн
	git pull
	$(COMPOSE) --profile production build
	$(COMPOSE) --profile production up -d
	$(COMPOSE) exec web $(PYTHON) setup.py install