"""
API-тест-кейсы (позитивные): API поиска Читай-города.

Базовый адрес — https://web-agr.chitai-gorod.ru/web/api. Авторизация
анонимная: POST /v1/auth/anonymous выдаёт Bearer-токен, фикстура
api_session передаёт его в заголовке Authorization.

Ответы в формате JSON:API: основной объект в data, связанные сущности
(товары, пагинация, подсказки) — в included. Структура ответов и значения
подтверждены живыми запросами перед написанием тестов (см. README).
"""
from typing import Any

import allure
import pytest
import requests

from config import (
    AUTHOR_QUERY,
    CHITAI_GOROD_API_URL,
    CUSTOMER_CITY_ID,
    REQUEST_TIMEOUT_S,
    SEARCH_QUERY,
    SUGGEST_PHRASE,
)

SEARCH_URL = f"{CHITAI_GOROD_API_URL}/v2/search/product"
SUGGESTS_URL = f"{CHITAI_GOROD_API_URL}/v2/search/search-phrase-suggests"
POPULAR_URL = f"{CHITAI_GOROD_API_URL}/v2/search/popular-search-phrases"


def _attach_response(response: requests.Response) -> None:
    allure.attach(
        f"{response.request.method} {response.url}\n\nHTTP {response.status_code}\n\n"
        f"{response.text[:3000]}",
        name="Ответ сервиса",
        attachment_type=allure.attachment_type.TEXT,
    )


def _included(body: dict[str, Any], item_type: str) -> list[dict[str, Any]]:
    return [item for item in body.get("included", []) if item.get("type") == item_type]


def _search(
    session: requests.Session, phrase: str, page: int = 1, per_page: int = 5
) -> requests.Response:
    params: dict[str, str | int] = {
        "phrase": phrase,
        "customerCityId": CUSTOMER_CITY_ID,
        "products[page]": page,
        "products[per-page]": per_page,
    }
    response = session.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT_S)
    _attach_response(response)
    return response


@pytest.mark.api
@allure.story("Авторизация")
@allure.title("Анонимная авторизация выдаёт Bearer-токен")
def test_anonymous_auth_returns_bearer_token() -> None:
    """POST /v1/auth/anonymous без логина и пароля выдаёт токен анонимного пользователя."""
    with allure.step("Отправить POST /v1/auth/anonymous с пустым телом"):
        response = requests.post(
            f"{CHITAI_GOROD_API_URL}/v1/auth/anonymous", json={}, timeout=REQUEST_TIMEOUT_S
        )
        allure.attach(
            f"HTTP {response.status_code}",
            name="Статус ответа (тело не прикладывается: в нём токен)",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Проверить статус 201, формат токена, группу пользователя и город"):
        assert response.status_code == 201
        body = response.json()
        assert body["token"]["accessToken"].startswith("Bearer ")
        assert body["user"]["group"] == "anonymous"
        assert isinstance(body["city"]["id"], int)


@pytest.mark.api
@allure.story("Поиск товаров")
@allure.title("Поиск по названию возвращает 5 товаров с названием и ценой")
def test_search_products_by_title(api_session: requests.Session) -> None:
    """Поиск «Гарри Поттер» с per-page=5 возвращает 5 товаров, среди них есть эта книга."""
    with allure.step(f"Отправить GET /v2/search/product?phrase={SEARCH_QUERY}, 5 на страницу"):
        response = _search(api_session, SEARCH_QUERY, page=1, per_page=5)

    with allure.step("Проверить статус 200 и тип результата"):
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["type"] == "searchProductResult"

    with allure.step("Проверить, что вернулось 5 товаров с названием и ценой больше нуля"):
        products = _included(body, "product")
        assert len(body["data"]["relationships"]["products"]["data"]) == 5
        assert len(products) == 5
        for product in products:
            assert product["attributes"]["title"]
            assert product["attributes"]["price"] > 0

    with allure.step("Проверить, что хотя бы одно название содержит поисковую фразу"):
        titles = [p["attributes"]["title"].lower() for p in products]
        assert any(SEARCH_QUERY.lower() in title for title in titles), titles


@pytest.mark.api
@allure.story("Поиск товаров")
@allure.title("Поиск по фамилии автора находит книги этого автора")
def test_search_products_by_author(api_session: requests.Session) -> None:
    """Поиск «Роулинг» возвращает товары, у которых среди авторов есть Роулинг."""
    with allure.step(f"Отправить GET /v2/search/product?phrase={AUTHOR_QUERY}"):
        response = _search(api_session, AUTHOR_QUERY, page=1, per_page=10)

    with allure.step("Проверить статус 200 и что у найденных книг есть автор с этой фамилией"):
        assert response.status_code == 200
        products = _included(response.json(), "product")
        assert products
        last_names = [
            author.get("lastName", "")
            for product in products
            for author in product["attributes"].get("authors") or []
        ]
        assert AUTHOR_QUERY in last_names, last_names


@pytest.mark.api
@allure.story("Поиск товаров")
@allure.title("Вторая страница выдачи возвращает 10 товаров и верную пагинацию")
def test_search_products_second_page(api_session: requests.Session) -> None:
    """products[page]=2 и products[per-page]=10 отражаются в блоке pagination."""
    with allure.step("Отправить GET /v2/search/product: страница 2, 10 товаров на страницу"):
        response = _search(api_session, AUTHOR_QUERY, page=2, per_page=10)

    with allure.step("Проверить статус 200, номер страницы, размер страницы и число товаров"):
        assert response.status_code == 200
        body = response.json()
        pagination = _included(body, "pagination")[0]["attributes"]
        assert pagination["current_page"] == 2
        assert pagination["per_page"] == 10
        assert pagination["total"] > 10
        assert len(_included(body, "product")) == 10


@pytest.mark.api
@allure.story("Подсказки поиска")
@allure.title("Подсказки по фразе «досто» содержат эту фразу")
def test_search_phrase_suggests(api_session: requests.Session) -> None:
    """GET /v2/search/search-phrase-suggests возвращает подсказки с введённой фразой."""
    with allure.step(f"Отправить GET /v2/search/search-phrase-suggests?phrase={SUGGEST_PHRASE}"):
        response = api_session.get(
            SUGGESTS_URL,
            params={"phrase": SUGGEST_PHRASE, "customerCityId": CUSTOMER_CITY_ID},
            timeout=REQUEST_TIMEOUT_S,
        )
        _attach_response(response)

    with allure.step("Проверить статус 200 и что каждая подсказка содержит фразу"):
        assert response.status_code == 200
        suggests = _included(response.json(), "searchPhraseSuggest")
        assert suggests
        for suggest in suggests:
            assert SUGGEST_PHRASE in suggest["attributes"]["plainPhrase"].lower()


@pytest.mark.api
@allure.story("Подсказки поиска")
@allure.title("Популярные поисковые фразы возвращаются непустым списком")
def test_popular_search_phrases(api_session: requests.Session) -> None:
    """GET /v2/search/popular-search-phrases возвращает список фраз с текстом."""
    with allure.step("Отправить GET /v2/search/popular-search-phrases"):
        response = api_session.get(
            POPULAR_URL, params={"customerCityId": CUSTOMER_CITY_ID}, timeout=REQUEST_TIMEOUT_S
        )
        _attach_response(response)

    with allure.step("Проверить статус 200, тип результата и текст каждой фразы"):
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["type"] == "popularSearchPhraseResult"
        phrases = _included(body, "popularSearchPhrase")
        assert phrases
        for phrase in phrases:
            assert phrase["attributes"]["phraseText"].strip()
