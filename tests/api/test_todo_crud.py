"""
API-тест-кейсы (позитивные): CRUD для Todo List API.

Сервис: JSONPlaceholder (https://jsonplaceholder.typicode.com/todos) —
публичный мок REST API, авторизация не требуется. Изменяющие запросы
(POST/PATCH/DELETE) не персистятся на сервере (это заглушка для обучения),
но реально выполняются по сети и возвращают настоящие HTTP-ответы —
именно это здесь и проверяется.

Поведение подтверждено вручную перед написанием тестов (см. README).
"""
import requests

import allure
import pytest

from config import TODO_API_BASE_URL, random_todo_title


@pytest.mark.api
@allure.story("CRUD задач")
@allure.title("GET списка задач возвращает непустой список")
def test_get_todos_list(api_session: requests.Session) -> None:
    """GET списка задач — должен вернуть непустой список."""
    with allure.step("Отправить GET /todos"):
        response = api_session.get(f"{TODO_API_BASE_URL}/todos")

    with allure.step("Проверить статус-код 200 и непустой список в ответе"):
        assert response.status_code == 200
        todos = response.json()
        assert isinstance(todos, list)
        assert len(todos) > 0


@pytest.mark.api
@allure.story("CRUD задач")
@allure.title("GET одной задачи возвращает все обязательные поля")
def test_get_single_todo(api_session: requests.Session) -> None:
    """GET одной существующей задачи — тело должно содержать обязательные поля."""
    with allure.step("Отправить GET /todos/1"):
        response = api_session.get(f"{TODO_API_BASE_URL}/todos/1")

    with allure.step("Проверить статус-код 200 и состав полей ответа"):
        assert response.status_code == 200
        todo = response.json()
        assert set(todo.keys()) == {"userId", "id", "title", "completed"}
        assert todo["id"] == 1


@pytest.mark.api
@allure.story("CRUD задач")
@allure.title("POST создания задачи возвращает 201 и эхо отправленных данных")
def test_create_todo(api_session: requests.Session) -> None:
    """POST новой задачи — сервер должен вернуть 201 и эхо отправленных данных."""
    title = random_todo_title()

    with allure.step(f"Отправить POST /todos с title='{title}'"):
        response = api_session.post(
            f"{TODO_API_BASE_URL}/todos",
            json={"title": title, "completed": False, "userId": 1},
        )

    with allure.step("Проверить статус-код 201 и тело ответа"):
        assert response.status_code == 201
        created = response.json()
        assert created["title"] == title
        assert created["completed"] is False
        assert "id" in created

    with allure.step("Сохранить id созданной задачи для последующих проверок"):
        allure.attach(
            str(created["id"]),
            name="created_todo_id",
            attachment_type=allure.attachment_type.TEXT,
        )


@pytest.mark.api
@allure.story("CRUD задач")
@allure.title("PATCH задачи обновляет поле title в ответе")
def test_update_todo_title(api_session: requests.Session) -> None:
    """PATCH задачи — обновлённое поле должно отражаться в ответе."""
    new_title = random_todo_title()

    with allure.step(f"Отправить PATCH /todos/1 с title='{new_title}'"):
        response = api_session.patch(
            f"{TODO_API_BASE_URL}/todos/1", json={"title": new_title}
        )

    with allure.step("Проверить статус-код 200 и обновлённый title в ответе"):
        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == new_title


@pytest.mark.api
@allure.story("CRUD задач")
@allure.title("DELETE задачи возвращает успешный статус")
def test_delete_todo(api_session: requests.Session) -> None:
    """DELETE задачи — должен вернуть успешный статус."""
    with allure.step("Отправить DELETE /todos/1"):
        response = api_session.delete(f"{TODO_API_BASE_URL}/todos/1")

    with allure.step("Проверить статус-код 200 или 204"):
        assert response.status_code in (200, 204)
