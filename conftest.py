"""
Общие фикстуры для API- и UI-тестов Читай-города.
"""
from typing import Generator

import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config import CHITAI_GOROD_API_URL, CHITAI_GOROD_BASE_URL, HEADLESS, REQUEST_TIMEOUT_S


# --------------------------------------------------------------------------
# API Читай-города: анонимный токен и сессия с заголовком Authorization
# --------------------------------------------------------------------------


@pytest.fixture(scope="session")
def api_token() -> str:
    """Анонимный Bearer-токен: сервис выдаёт его без логина и пароля."""
    response = requests.post(
        f"{CHITAI_GOROD_API_URL}/v1/auth/anonymous", json={}, timeout=REQUEST_TIMEOUT_S
    )
    response.raise_for_status()
    token: str = response.json()["token"]["accessToken"]
    return token


@pytest.fixture(scope="session")
def api_session(api_token: str) -> Generator[requests.Session, None, None]:
    """requests.Session с токеном в заголовке Authorization для всех API-тестов."""
    session = requests.Session()
    session.headers.update({"Authorization": api_token, "Accept": "application/json"})
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
