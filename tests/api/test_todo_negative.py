"""
API-тест-кейсы (негативные): Todo List API (JSONPlaceholder).

JSONPlaceholder — мок-сервис: он не валидирует тела запросов и всегда
отвечает "успехом" на POST/PATCH/DELETE, даже для мусорных данных. Поэтому
негативные проверки здесь ограничены тем, что сервис реально проверяет
(несуществующий id при GET/DELETE через отдельный путь) и тем, что можно
проверить в структуре ответа (сервис не подставляет отсутствующее
обязательное поле "title" сам). Поведение подтверждено вручную перед
написанием тестов (см. README).

Число негативных тест-кейсов (3) не превышает число позитивных (5) —
требование диплома.
"""
import requests

import allure
import pytest

from config import TODO_API_BASE_URL


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
@allure.title("POST без обязательного поля title не возвращает title в ответе")
def test_create_todo_without_title_has_no_title_in_response(
    api_session: requests.Session,
) -> None:
    """
    Создание задачи без обязательного поля title: сервис не выдаёт ошибку
    (мок принимает любое тело), но и не подставляет title сам — в ответе
    поля "title" быть не должно. Это фиксирует реальное поведение сервиса
    и защищает от регрессии, если в будущем это изменится.
    """
    with allure.step("Отправить POST /todos без поля title"):
        response = api_session.post(
            f"{TODO_API_BASE_URL}/todos", json={"completed": False, "userId": 1}
        )

    with allure.step("Проверить статус-код 201 и отсутствие поля title в ответе"):
        assert response.status_code == 201
        created = response.json()
        assert "title" not in created
