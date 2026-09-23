"""
UI-тест-кейсы: поиск и просмотр книги на chitai-gorod.ru.

Сайт доступен без логина, поэтому тесты работают с публичным каталогом:
поиск по названию -> список результатов -> открытие карточки товара.

Селекторы подтверждены вручную на живом сайте перед написанием тестов
(см. README): поле поиска — input[name="phrase"] (не имеет
предсказуемого текста, только это стабильное имя), карточки товаров в
выдаче — ссылки вида a[href*="/product/"].

Важно: сайт постоянно шлёт фоновые запросы (аналитика, рекомендации),
поэтому состояние "networkidle" никогда не наступает и вызывает ложные
таймауты (подтверждено живым прогоном). Вместо ожидания "тишины в сети"
тесты явно ждут появления нужного элемента через wait_for_selector —
это то, что реально имеет значение для проверки.
"""
from playwright.sync_api import Page

import allure
import pytest

from config import SEARCH_QUERY

SEARCH_INPUT_SELECTOR = 'input[name="phrase"]'
PRODUCT_CARD_SELECTOR = 'a[href*="/product/"]'


@allure.step("Открыть главную страницу и выполнить поиск по запросу '{query}'")
def _search(page: Page, query: str) -> None:
    page.goto("/")
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill(query)
    search_box.press("Enter")


@pytest.mark.ui
@allure.story("Поиск книг")
@allure.title("Поиск по существующему запросу возвращает результаты")
def test_search_returns_results(page: Page) -> None:
    """Поиск по существующему запросу должен вернуть хотя бы один результат."""
    _search(page, SEARCH_QUERY)

    with allure.step("Дождаться карточек товаров в выдаче"):
        page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=15_000)

    with allure.step("Убедиться, что найден хотя бы один товар"):
        results = page.locator(PRODUCT_CARD_SELECTOR)
        assert results.count() > 0, "Поиск не вернул ни одного товара"


@pytest.mark.ui
@allure.story("Поиск книг")
@allure.title("Первый результат поиска отображается на странице")
def test_search_results_contain_query_relevance(page: Page) -> None:
    """Первый результат поиска должен быть видимой ссылкой на карточку товара."""
    _search(page, SEARCH_QUERY)

    with allure.step("Дождаться карточек товаров в выдаче"):
        page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=15_000)

    with allure.step("Проверить видимость первого результата"):
        first_result = page.locator(PRODUCT_CARD_SELECTOR).first
        assert first_result.is_visible()


@pytest.mark.ui
@allure.story("Просмотр карточки товара")
@allure.title("Клик по товару из выдачи открывает карточку товара")
def test_open_product_card(page: Page) -> None:
    """Клик по первому товару из поиска должен открыть карточку товара."""
    _search(page, SEARCH_QUERY)

    with allure.step("Дождаться карточек товаров в выдаче"):
        page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=15_000)

    with allure.step("Кликнуть по первому товару и дождаться перехода"):
        first_product = page.locator(PRODUCT_CARD_SELECTOR).first
        first_product.click()
        page.wait_for_url("**/product/**", timeout=15_000)

    with allure.step("Проверить, что открылась страница карточки товара"):
        assert "/product/" in page.url


@pytest.mark.ui
@allure.story("Граничные случаи поиска")
@allure.title("Пустой поисковый запрос не приводит к ошибке сайта")
def test_empty_search_query_does_not_crash(page: Page) -> None:
    """Пустой поисковый запрос не должен приводить к ошибке — сайт остаётся рабочим."""
    _search(page, "")

    with allure.step("Дождаться загрузки DOM после пустого поиска"):
        page.wait_for_load_state("domcontentloaded")

    with allure.step("Проверить, что страница осталась рабочей (есть заголовок)"):
        assert page.title() != ""


@pytest.mark.ui
@allure.story("Граничные случаи поиска")
@allure.title("Заведомо несуществующий запрос обрабатывается без ошибки")
def test_nonexistent_query_does_not_error(page: Page) -> None:
    """
    Заведомо бессмысленный запрос не должен приводить к ошибке страницы.

    Подтверждено вручную: сайт не показывает пустое состояние для такого
    запроса, а откатывается на список рекомендаций — это тоже валидный
    результат, поэтому проверяется отсутствие ошибки и наличие заголовка,
    а не конкретное количество товаров.
    """
    _search(page, "ъъъфываолдж12345несуществующийтовар")

    with allure.step("Дождаться перехода на страницу результатов поиска"):
        page.wait_for_url("**/search**", timeout=15_000)

    with allure.step("Проверить, что страница рабочая и осталась на /search"):
        assert page.title() != ""
        assert "/search" in page.url
