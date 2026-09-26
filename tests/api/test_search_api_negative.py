"""
API-тест-кейсы (негативные): API поиска Читай-города.

Каждая проверка опирается на реальную валидацию сервиса: он отвечает
ошибками 401, 400, 422 и 405 с понятным текстом. Коды и тексты ошибок
подтверждены живыми запросами перед написанием тестов (см. README).

Последний тест фиксирует найденный дефект BR-003: несуществующий
customerCityId приводит к ошибке сервера 500 вместо ошибки клиента 4xx.
Он помечен xfail(strict=True): пока дефект не исправлен, тест
ожидаемо падает, а после исправления pytest сообщит об этом.

Негативных тест-кейсов (5) меньше, чем позитивных (6), — требование диплома.
"""
import allure
import pytest
import requests

from config import (
    CHITAI_GOROD_API_URL,
    CUSTOMER_CITY_ID,
    NONEXISTENT_CITY_ID,
    REQUEST_TIMEOUT_S,
    SEARCH_QUERY,
)

SEARCH_URL = f"{CHITAI_GOROD_API_URL}/v2/search/product"


def _attach_response(response: requests.Response) -> None:
    allure.attach(
        f"{response.request.method} {response.url}\n\nHTTP {response.status_code}\n\n"
        f"{response.text[:3000]}",
        name="Ответ сервиса",
        attachment_type=allure.attachment_type.TEXT,
    )


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("Поиск без заголовка Authorization возвращает 401")
def test_search_without_token_returns_401() -> None:
    """Запрос без токена отклоняется с 401 и сообщением об обязательном заголовке."""
    with allure.step("Отправить GET /v2/search/product без заголовка Authorization"):
        response = requests.get(
            SEARCH_URL,
            params={"phrase": SEARCH_QUERY, "customerCityId": CUSTOMER_CITY_ID},
            headers={"Accept": "application/json"},
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить статус 401 и текст ошибки"):
        assert response.status_code == 401
        assert response.json()["message"] == "Authorization обязательное поле"


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("Поиск по фразе из одного символа возвращает 400")
def test_search_with_one_char_phrase_returns_400(api_session: requests.Session) -> None:
    """Фраза короче 2 символов не проходит валидацию поля Phrase."""
    with allure.step("Отправить GET /v2/search/product?phrase=a"):
        response = api_session.get(
            SEARCH_URL,
            params={"phrase": "a", "customerCityId": CUSTOMER_CITY_ID},
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить статус 400, поле с ошибкой и текст ошибки"):
        assert response.status_code == 400
        error = response.json()["errors"][0]
        assert error["source"]["pointer"] == "GetSearchProductParams.Phrase"
        assert "минимум 2 символа" in error["title"]


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("Отрицательный номер страницы возвращает 422")
def test_search_with_negative_page_returns_422(api_session: requests.Session) -> None:
    """products[page]=-1 отклоняется: номер страницы должен быть положительным."""
    with allure.step("Отправить GET /v2/search/product с products[page]=-1"):
        response = api_session.get(
            SEARCH_URL,
            params={
                "phrase": SEARCH_QUERY,
                "customerCityId": CUSTOMER_CITY_ID,
                "products[page]": -1,
            },
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить статус 422, поле с ошибкой и текст ошибки"):
        assert response.status_code == 422
        error = response.json()["errors"][0]
        assert error["source"]["pointer"] == "/results/page"
        assert error["title"] == "Значение должно быть положительным."


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("Метод POST для поиска не поддерживается: 405")
def test_search_with_post_method_returns_405(api_session: requests.Session) -> None:
    """Поиск доступен только методом GET, POST отклоняется с 405."""
    with allure.step("Отправить POST /v2/search/product"):
        response = api_session.post(
            SEARCH_URL,
            params={"phrase": SEARCH_QUERY, "customerCityId": CUSTOMER_CITY_ID},
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить статус 405"):
        assert response.status_code == 405


@pytest.mark.api
@allure.story("Негативные сценарии")
@allure.title("Несуществующий customerCityId должен давать ошибку клиента 4xx (BR-003)")
@pytest.mark.xfail(
    strict=True,
    reason="BR-003: на несуществующий customerCityId сервис отвечает 500 вместо 4xx",
)
def test_search_with_nonexistent_city_returns_client_error(
    api_session: requests.Session,
) -> None:
    """Несуществующий город — ошибка клиента: ожидается 4xx, а не падение сервера."""
    with allure.step(f"Отправить GET /v2/search/product?customerCityId={NONEXISTENT_CITY_ID}"):
        response = api_session.get(
            SEARCH_URL,
            params={"phrase": SEARCH_QUERY, "customerCityId": NONEXISTENT_CITY_ID},
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить, что статус ответа — ошибка клиента 4xx"):
        assert 400 <= response.status_code < 500, (
            f"Ожидалась ошибка клиента 4xx, получено {response.status_code}"
        )
