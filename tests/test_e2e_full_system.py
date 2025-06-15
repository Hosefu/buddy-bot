import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from apps.users.models import User, Role
from apps.flows.models import (
    Flow, FlowStep, UserFlow, UserStepProgress, Task, Quiz, QuizQuestion, QuizAnswer, FlowBuddy
)
from apps.guides.models import Article

pytestmark = pytest.mark.django_db


def log_request(report_data, name, method, url, response, request_body=None):
    """Helper to store step info for HTML report."""
    try:
        response_data = response.json()
    except Exception:  # pragma: no cover - non JSON
        response_data = response.content.decode("utf-8")
    report_data.append({
        "name": name,
        "method": method,
        "url": url,
        "request_body": request_body,
        "response_body": response_data,
        "status_code": response.status_code,
    })


def test_e2e_03_full_system(
    api_client: APIClient,
    admin_user: User,
    buddy_user: User,
    user_factory,
    report_data: list,
):
    """E2E-03: полный сценарий модератора, бадди и пользователя."""
    learner = user_factory(telegram_id="501", name="Learner")
    buddy2 = user_factory(role=Role.RoleChoices.BUDDY, telegram_id="502", name="Second Buddy")

    # --- Moderator creates flow and steps ---
    api_client.force_authenticate(user=admin_user)
    bad_resp = api_client.post("/api/admin/flows/", {}, format="json")
    assert bad_resp.status_code == 400
    log_request(report_data, "Создание потока с ошибкой", "POST", "/api/admin/flows/", bad_resp, {})

    flow_data = {"title": "Онбординг", "description": "Добро пожаловать"}
    resp = api_client.post("/api/admin/flows/", flow_data, format="json")
    assert resp.status_code == 201
    flow_id = resp.data["id"]
    log_request(report_data, "Создание потока", "POST", "/api/admin/flows/", resp, flow_data)

    step_titles = ["Введение", "Задание", "Контроль знаний"]
    step_ids = []
    for title in step_titles:
        data = {"title": title, "description": f"Этап {title}"}
        resp = api_client.post(f"/api/admin/flows/{flow_id}/steps/", data, format="json")
        assert resp.status_code == 201
        step_ids.append(resp.data["id"])
        log_request(report_data, f"Создание шага {title}", "POST", f"/api/admin/flows/{flow_id}/steps/", resp, data)

    # attach content directly (admin endpoints отсутствуют)
    Article.objects.create(
        title="Приветствие", slug="intro", content="Статья", flow_step_id=step_ids[0],
        author=admin_user, is_published=True, published_at=timezone.now()
    )
    Task.objects.create(
        flow_step_id=step_ids[1], title="Первое задание", description="Сделай A", instruction="Ищи код", code_word="word"
    )
    quiz = Quiz.objects.create(flow_step_id=step_ids[2], title="Мини тест", passing_score_percentage=100)
    question = QuizQuestion.objects.create(quiz=quiz, question="2+2?", order=1)
    correct = QuizAnswer.objects.create(question=question, answer_text="4", is_correct=True, explanation="Верно", order=1)
    wrong = QuizAnswer.objects.create(question=question, answer_text="5", is_correct=False, explanation="Нет", order=2)

    # назначим второму бадди роль через API
    role_assign_url = f"/api/auth/users/{buddy2.id}/roles/"
    resp = api_client.post(role_assign_url, {"role_id": Role.objects.get(name=Role.RoleChoices.BUDDY).id}, format="json")
    assert resp.status_code in (200, 201)
    log_request(report_data, "Назначение роли buddy", "POST", role_assign_url, resp, {"role_id": Role.objects.get(name=Role.RoleChoices.BUDDY).id})

    # --- Buddy starts flow ---
    api_client.force_authenticate(user=buddy_user)
    start_data = {"user_id": learner.id, "additional_buddies": [buddy2.id]}
    resp = api_client.post(f"/api/buddy/flows/{flow_id}/start/", start_data, format="json")
    assert resp.status_code == 201
    user_flow_id = UserFlow.objects.get(user=learner, flow_id=flow_id).id
    log_request(report_data, "Старт флоу", "POST", f"/api/buddy/flows/{flow_id}/start/", resp, start_data)

    # повторный запуск должен дать 409
    resp2 = api_client.post(f"/api/buddy/flows/{flow_id}/start/", start_data, format="json")
    assert resp2.status_code == 409
    log_request(report_data, "Повторный запуск", "POST", f"/api/buddy/flows/{flow_id}/start/", resp2, start_data)

    # пауза и возобновление
    resp = api_client.post(f"/api/buddy/flows/{user_flow_id}/pause/", {"reason": "break"}, format="json")
    assert resp.status_code == 200
    log_request(report_data, "Пауза флоу", "POST", f"/api/buddy/flows/{user_flow_id}/pause/", resp, {"reason": "break"})

    resp = api_client.post(f"/api/buddy/flows/{user_flow_id}/resume/", {}, format="json")
    assert resp.status_code == 200
    log_request(report_data, "Возобновление флоу", "POST", f"/api/buddy/flows/{user_flow_id}/resume/", resp, {})

    # --- Second buddy checks progress ---
    api_client.force_authenticate(user=buddy2)
    resp = api_client.get(f"/api/buddy/flows/{user_flow_id}/")
    assert resp.status_code == 200
    log_request(report_data, "Просмотр прогресса бадди", "GET", f"/api/buddy/flows/{user_flow_id}/", resp)

    # --- User goes through the flow ---
    api_client.force_authenticate(user=learner)

    # Step 1 Article
    resp = api_client.post(f"/api/flows/{flow_id}/steps/{step_ids[0]}/read/")
    assert resp.status_code == 200
    log_request(report_data, "Чтение статьи", "POST", f"/api/flows/{flow_id}/steps/{step_ids[0]}/read/", resp)

    prog = api_client.get(f"/api/my/progress/{flow_id}/")
    log_request(report_data, "Проверка прогресса после статьи", "GET", f"/api/my/progress/{flow_id}/", prog)

    # Step 2 Task
    resp = api_client.get(f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/")
    assert resp.status_code == 200
    log_request(report_data, "Получение задания", "GET", f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/", resp)

    wrong_ans = api_client.post(
        f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/", {"answer": "no"}, format="json")
    assert wrong_ans.status_code == 200 and not wrong_ans.data["is_correct"]
    log_request(report_data, "Неверный ответ", "POST", f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/", wrong_ans, {"answer": "no"})

    correct_ans = api_client.post(
        f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/", {"answer": "word"}, format="json")
    assert correct_ans.status_code == 200 and correct_ans.data["is_correct"]
    log_request(report_data, "Верный ответ", "POST", f"/api/flows/{flow_id}/steps/{step_ids[1]}/task/", correct_ans, {"answer": "word"})

    prog = api_client.get(f"/api/my/progress/{flow_id}/")
    log_request(report_data, "Проверка прогресса после задания", "GET", f"/api/my/progress/{flow_id}/", prog)

    # Step 3 Quiz
    resp = api_client.get(f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/")
    assert resp.status_code == 200
    log_request(report_data, "Получение квиза", "GET", f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/", resp)

    wrong_q = api_client.post(
        f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/{question.id}/", {"answer_id": wrong.id}, format="json")
    assert wrong_q.status_code == 200 and not wrong_q.data["is_correct"]
    log_request(report_data, "Ответ на квиз неверный", "POST", f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/{question.id}/", wrong_q, {"answer_id": wrong.id})

    correct_q = api_client.post(
        f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/{question.id}/", {"answer_id": correct.id}, format="json")
    assert correct_q.status_code == 200 and correct_q.data["is_correct"]
    log_request(report_data, "Ответ на квиз верный", "POST", f"/api/flows/{flow_id}/steps/{step_ids[2]}/quiz/{question.id}/", correct_q, {"answer_id": correct.id})

    final = api_client.get(f"/api/my/progress/{flow_id}/")
    log_request(report_data, "Финальный прогресс", "GET", f"/api/my/progress/{flow_id}/", final)
    assert final.data["status"] == "completed"
