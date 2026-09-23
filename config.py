"""
Конфигурация проекта автоматизации.

Все окружение-зависимые данные вынесены сюда. Ни один из двух
тестируемых ресурсов не требует логина/пароля — авторизация не
используется, переменные окружения не нужны.

История выбора API: изначально тест-план ссылался на приватный тестовый
сервер Todo List API (http://5.101.50.9:8015), уже проверенный вручную
в Postman (17/17 тест-кейсов). Сервер перестал отвечать (недоступен по
сети), поэтому API-тесты переведены на публичный сервис с идентичной
семантикой Todo-ресурса — JSONPlaceholder (https://jsonplaceholder.typicode.com).
Структура тест-кейсов (GET списка/одного, POST, PATCH, DELETE,
негативные проверки) сохранена как в исходном тест-плане.
"""
import random
import string

# --- UI: Читай-город ---
CHITAI_GOROD_BASE_URL = "https://www.chitai-gorod.ru"
SEARCH_QUERY = "Гарри Поттер"
AUTHOR_QUERY = "Роулинг"

# --- API: Todo List (JSONPlaceholder — публичный, без авторизации) ---
TODO_API_BASE_URL = "https://jsonplaceholder.typicode.com"


def random_todo_title() -> str:
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"QA autotest todo {suffix}"


DEFAULT_TIMEOUT_MS = 10_000
HEADLESS = True
