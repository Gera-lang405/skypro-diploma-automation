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

import pytest

from config import TODO_API_BASE_URL, random_todo_title


@pytest.mark.api
def test_get_todos_list(api_session: requests.Session) -> None:
    """GET списка задач — должен вернуть непустой список."""
    response = api_session.get(f"{TODO_API_BASE_URL}/todos")
    assert response.status_code == 200
    todos = response.json()
    assert isinstance(todos, list)
    assert len(todos) > 0


@pytest.mark.api
def test_get_single_todo(api_session: requests.Session) -> None:
    """GET одной существующей задачи — тело должно содержать обязательные поля."""
    response = api_session.get(f"{TODO_API_BASE_URL}/todos/1")
    assert response.status_code == 200
    todo = response.json()
    assert set(todo.keys()) == {"userId", "id", "title", "completed"}
    assert todo["id"] == 1


@pytest.mark.api
def test_create_todo(api_session: requests.Session) -> None:
    """POST новой задачи — сервер должен вернуть 201 и эхо отправленных данных."""
    title = random_todo_title()
    response = api_session.post(
        f"{TODO_API_BASE_URL}/todos",
        json={"title": title, "completed": False, "userId": 1},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == title
    assert created["completed"] is False
    assert "id" in created


@pytest.mark.api
def test_update_todo_title(api_session: requests.Session) -> None:
    """PATCH задачи — обновлённое поле должно отражаться в ответе."""
    new_title = random_todo_title()
    response = api_session.patch(
        f"{TODO_API_BASE_URL}/todos/1", json={"title": new_title}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == new_title


@pytest.mark.api
def test_delete_todo(api_session: requests.Session) -> None:
    """DELETE задачи — должен вернуть успешный статус."""
    response = api_session.delete(f"{TODO_API_BASE_URL}/todos/1")
    assert response.status_code in (200, 204)
