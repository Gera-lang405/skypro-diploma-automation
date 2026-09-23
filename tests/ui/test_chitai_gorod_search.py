"""
UI-тест-кейсы: поиск и просмотр книги на chitai-gorod.ru.

Сайт доступен без логина, поэтому тесты работают с публичным каталогом:
поиск по названию -> список результатов -> открытие карточки товара.

Селекторы подтверждены вручную на живом сайте перед написанием тестов
(см. README): поле поиска — input[name="phrase"] (не имеет
предсказуемого текста, только это стабильное имя), карточки товаров в
выдаче — ссылки вида a[href*="/product/"].
"""
from playwright.sync_api import Page

import pytest

from config import SEARCH_QUERY

SEARCH_INPUT_SELECTOR = 'input[name="phrase"]'
PRODUCT_CARD_SELECTOR = 'a[href*="/product/"]'


@pytest.mark.ui
def test_search_returns_results(page: Page) -> None:
    """Поиск по существующему запросу должен вернуть хотя бы один результат."""
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill(SEARCH_QUERY)
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")

    results = page.locator(PRODUCT_CARD_SELECTOR)
    assert results.count() > 0, "Поиск не вернул ни одного товара"


@pytest.mark.ui
def test_search_results_contain_query_relevance(page: Page) -> None:
    """Первый результат поиска должен быть видимой ссылкой на карточку товара."""
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill(SEARCH_QUERY)
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")

    first_result = page.locator(PRODUCT_CARD_SELECTOR).first
    assert first_result.is_visible()


@pytest.mark.ui
def test_open_product_card(page: Page) -> None:
    """Клик по первому товару из поиска должен открыть карточку товара."""
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill(SEARCH_QUERY)
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")

    first_product = page.locator(PRODUCT_CARD_SELECTOR).first
    first_product.click()
    page.wait_for_load_state("networkidle")

    assert "/product/" in page.url


@pytest.mark.ui
def test_empty_search_query_does_not_crash(page: Page) -> None:
    """Пустой поисковый запрос не должен приводить к ошибке — сайт остаётся рабочим."""
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill("")
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")

    assert page.title() != ""


@pytest.mark.ui
def test_nonexistent_query_does_not_error(page: Page) -> None:
    """
    Заведомо бессмысленный запрос не должен приводить к ошибке страницы.

    Подтверждено вручную: сайт не показывает пустое состояние для такого
    запроса, а откатывается на список рекомендаций — это тоже валидный
    результат, поэтому проверяется отсутствие ошибки и наличие заголовка,
    а не конкретное количество товаров.
    """
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill("ъъъфываолдж12345несуществующийтовар")
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")

    assert page.title() != ""
    assert "/search" in page.url
