"""
Общие фикстуры для API- (Todo List) и UI- (Читай-город) тестов.
"""
from typing import Generator

import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config import CHITAI_GOROD_BASE_URL, HEADLESS, TODO_API_BASE_URL


# --------------------------------------------------------------------------
# API (Todo List / JSONPlaceholder) фикстуры — авторизация не требуется
# --------------------------------------------------------------------------


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return TODO_API_BASE_URL


@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    """requests.Session с общим Content-Type для всех API-тестов."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


# --------------------------------------------------------------------------
# UI (Читай-город) фикстуры
# --------------------------------------------------------------------------


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    browser_instance = playwright_instance.chromium.launch(headless=HEADLESS)
    yield browser_instance
    browser_instance.close()


@pytest.fixture
def page(browser: Browser) -> Generator[Page, None, None]:
    """Новая изолированная страница на каждый тест — тесты не влияют друг на друга."""
    context: BrowserContext = browser.new_context(base_url=CHITAI_GOROD_BASE_URL)
    new_page = context.new_page()
    yield new_page
    context.close()
