"""
API-тест-кейсы (негативные): Todo List API (JSONPlaceholder).

JSONPlaceholder — учебный мок-сервис: тела запросов он не валидирует.
Поэтому негативные проверки построены на том, что сервис реально
проверяет: несуществующий id, id неверного формата и неподдерживаемый
метод (POST на адрес конкретной задачи). Каждый статус-код подтверждён
живым запросом перед написанием тестов (см. README).

Число негативных тест-кейсов (3) не превышает число позитивных (5) —
требование диплома.
"""
import requests

import allure
import pytest

from config import TODO_API_BASE_URL, random_todo_title


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("GET несуществующей задачи возвращает 404")
def test_get_nonexistent_todo_returns_404(api_session: requests.Session) -> None:
    """GET несуществующей задачи должен вернуть 404."""
    with allure.step("Отправить GET /todos/999999 (несуществующий id)"):
        response = api_session.get(f"{TODO_API_BASE_URL}/todos/999999")

    with allure.step("Проверить статус-код 404"):
        assert response.status_code == 404


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("GET задачи по нечисловому id возвращает 404, а не 500")
def test_get_todo_with_invalid_id_format_returns_404(
    api_session: requests.Session,
) -> None:
    """GET задачи по нечисловому id должен вернуть 404, а не 500/200."""
    with allure.step("Отправить GET /todos/not-a-number"):
        response = api_session.get(f"{TODO_API_BASE_URL}/todos/not-a-number")

    with allure.step("Проверить статус-код 404"):
        assert response.status_code == 404


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("POST на адрес конкретной задачи (неподдерживаемый метод) возвращает 404")
def test_post_to_single_todo_is_not_supported(api_session: requests.Session) -> None:
    """POST на /todos/{id} сервис не поддерживает: ожидается 404, а не 200/201."""
    with allure.step("Отправить POST /todos/1 с телом новой задачи"):
        response = api_session.post(
            f"{TODO_API_BASE_URL}/todos/1", json={"title": random_todo_title()}
        )

    with allure.step("Проверить статус-код 404"):
        assert response.status_code == 404
