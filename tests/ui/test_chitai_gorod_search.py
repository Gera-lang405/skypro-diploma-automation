"""
UI-тест-кейсы (позитивные): поиск книги и просмотр карточки товара на chitai-gorod.ru.

Сайт доступен без логина, поэтому тесты работают с публичным каталогом:
поиск -> страница результатов /search -> карточка товара /product/.

Селекторы подтверждены вручную на живом сайте перед написанием тестов
(см. README):
- поле поиска — input[name="phrase"];
- карточки товаров в выдаче — ссылки a[href*="/product/"] внутри блока
  .app-products-list. Просто a[href*="/product/"] брать нельзя: такие же
  ссылки есть на главной странице и в скрытом выпадающем списке подсказок
  поиска, и тест мог бы «найти» товары без выполнения поиска;
- заголовок выдачи — h1.search-title__head;
- название товара в карточке — h1.product-detail-page__title;
- открытый список подсказок поиска — .app-search--opened, пункты
  подсказок — .search-suggests-modal__suggests-list .suggests-list__item.

Сайт постоянно шлёт фоновые запросы (аналитика, рекомендации), поэтому
состояние "networkidle" не наступает. Вместо этого используются явные
ожидания: wait_for_url, wait_for_selector и expect из Playwright.
"""
from playwright.sync_api import Page, expect

import allure
import pytest

from config import AUTHOR_QUERY, SEARCH_QUERY

SEARCH_INPUT_SELECTOR = 'input[name="phrase"]'
PRODUCT_CARD_SELECTOR = '.app-products-list a[href*="/product/"]'
RESULTS_TITLE_SELECTOR = "h1.search-title__head"
PRODUCT_TITLE_SELECTOR = "h1.product-detail-page__title"
SEARCH_SUGGESTIONS_OPENED_SELECTOR = ".app-search--opened"
SEARCH_SUGGESTION_ITEM_SELECTOR = ".search-suggests-modal__suggests-list .suggests-list__item"
APP_MOUNTED_SCRIPT = "() => Boolean(document.querySelector('#__nuxt')?.__vue_app__)"
WAIT_TIMEOUT_MS = 15_000


@allure.step("Открыть главную страницу и выполнить поиск по запросу '{query}'")
def _search(page: Page, query: str) -> None:
    page.goto("/")
    # Дождаться, пока клиентское приложение смонтируется: иначе введённый
    # текст может сброситься при гидратации страницы.
    page.wait_for_function(APP_MOUNTED_SCRIPT, timeout=WAIT_TIMEOUT_MS)
    search_box = page.locator(SEARCH_INPUT_SELECTOR)
    search_box.fill(query)
    expect(search_box).to_have_value(query)
    # Как пользователь: дождаться подсказок по введённому запросу и только
    # потом нажать Enter. Так запрос точно попал в состояние страницы, а
    # поздний ответ подсказок не откроет список поверх выдачи.
    expect(page.locator(SEARCH_SUGGESTION_ITEM_SELECTOR).first).to_be_visible(
        timeout=WAIT_TIMEOUT_MS
    )
    search_box.press("Enter")
    page.wait_for_url(
        "**/search**", wait_until="domcontentloaded", timeout=WAIT_TIMEOUT_MS
    )
    # Закрыть список подсказок, чтобы он не перехватывал клики по выдаче.
    page.keyboard.press("Escape")
    expect(page.locator(SEARCH_SUGGESTIONS_OPENED_SELECTOR)).to_have_count(
        0, timeout=WAIT_TIMEOUT_MS
    )


@allure.step("Дождаться карточек товаров в выдаче")
def _wait_for_results(page: Page) -> None:
    page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=WAIT_TIMEOUT_MS)


@pytest.mark.ui
@allure.story("Поиск книг")
@allure.title("Поиск по названию книги возвращает результаты")
def test_search_returns_results(page: Page) -> None:
    """Поиск по названию книги должен вернуть хотя бы один товар."""
    _search(page, SEARCH_QUERY)
    _wait_for_results(page)

    with allure.step("Убедиться, что найден хотя бы один товар"):
        results = page.locator(PRODUCT_CARD_SELECTOR)
        assert results.count() > 0, "Поиск не вернул ни одного товара"


@pytest.mark.ui
@allure.story("Поиск книг")
@allure.title("Первый результат поиска отображается на странице")
def test_first_search_result_is_visible(page: Page) -> None:
    """Первый результат поиска должен быть видимой ссылкой на карточку товара."""
    _search(page, SEARCH_QUERY)
    _wait_for_results(page)

    with allure.step("Проверить видимость первого результата"):
        first_result = page.locator(PRODUCT_CARD_SELECTOR).first
        expect(first_result).to_be_visible()


@pytest.mark.ui
@allure.story("Поиск книг")
@allure.title("Поиск по фамилии автора возвращает результаты")
def test_search_by_author_returns_results(page: Page) -> None:
    """Поиск по фамилии автора должен показать запрос в заголовке выдачи и найти товары."""
    _search(page, AUTHOR_QUERY)
    _wait_for_results(page)

    with allure.step("Проверить, что заголовок выдачи содержит фамилию автора"):
        heading = page.locator(RESULTS_TITLE_SELECTOR)
        expect(heading).to_contain_text(AUTHOR_QUERY, ignore_case=True)

    with allure.step("Убедиться, что найден хотя бы один товар"):
        assert page.locator(PRODUCT_CARD_SELECTOR).count() > 0


@pytest.mark.ui
@allure.story("Просмотр карточки товара")
@allure.title("Клик по товару из выдачи открывает карточку товара")
def test_open_product_card(page: Page) -> None:
    """Клик по первому товару из поиска должен открыть карточку товара."""
    _search(page, SEARCH_QUERY)
    _wait_for_results(page)

    with allure.step("Кликнуть по первому товару и дождаться перехода"):
        page.locator(PRODUCT_CARD_SELECTOR).first.click()
        page.wait_for_url(
            "**/product/**", wait_until="domcontentloaded", timeout=WAIT_TIMEOUT_MS
        )

    with allure.step("Проверить, что открылась страница карточки товара"):
        assert "/product/" in page.url


@pytest.mark.ui
@allure.story("Просмотр карточки товара")
@allure.title("Карточка товара отображает название книги")
def test_product_card_shows_title(page: Page) -> None:
    """В открытой карточке товара должно отображаться непустое название книги."""
    _search(page, SEARCH_QUERY)
    _wait_for_results(page)

    with allure.step("Открыть карточку первого товара из выдачи"):
        page.locator(PRODUCT_CARD_SELECTOR).first.click()
        page.wait_for_url(
            "**/product/**", wait_until="domcontentloaded", timeout=WAIT_TIMEOUT_MS
        )

    with allure.step("Проверить, что название товара отображается и не пустое"):
        title = page.locator(PRODUCT_TITLE_SELECTOR)
        expect(title).to_be_visible(timeout=WAIT_TIMEOUT_MS)
        assert title.inner_text().strip() != ""
