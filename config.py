"""
Конфигурация проекта автоматизации.

Все адреса и тестовые данные вынесены сюда. Логин и пароль не нужны:
UI-тесты работают в гостевом режиме, а API Читай-города сам выдаёт
анонимный Bearer-токен (POST /web/api/v1/auth/anonymous).
"""

# --- UI: Читай-город ---
CHITAI_GOROD_BASE_URL = "https://www.chitai-gorod.ru"
SEARCH_QUERY = "Гарри Поттер"
AUTHOR_QUERY = "Роулинг"

# --- API: Читай-город ---
CHITAI_GOROD_API_URL = "https://web-agr.chitai-gorod.ru/web/api"
CUSTOMER_CITY_ID = 213  # Москва — город, который сервис выдаёт анонимному пользователю
NONEXISTENT_CITY_ID = 99999  # такого города нет в справочнике
SUGGEST_PHRASE = "досто"
REQUEST_TIMEOUT_S = 15

# --- Общее ---
DEFAULT_TIMEOUT_MS = 10_000
HEADLESS = True
