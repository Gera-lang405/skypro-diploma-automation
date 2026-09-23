# Дипломная работа — автоматизация тестирования

Проект автоматизации для дипломной работы по профессии «Инженер по тестированию» (Sky.Pro).

## Тестируемые приложения

- **UI:** каталог книжного магазина **Читай-город** — https://www.chitai-gorod.ru (публичный доступ, без логина — поиск, открытие карточки товара).
- **API:** **Todo List API** — https://jsonplaceholder.typicode.com/todos (публичный мок-сервис, без авторизации).

Изначально API-часть тест-плана была рассчитана на приватный тестовый сервер (`http://5.101.50.9:8015`), уже вручную проверенный в Postman (17/17 тест-кейсов). Сервер перестал отвечать по сети, поэтому API-тесты переведены на публичный сервис с идентичной семантикой Todo-ресурса (GET списка/одного, POST, PATCH, DELETE) — структура тест-кейсов из тест-плана сохранена без изменений.

## Ключевые функции, покрытые тестами

1. **Поиск и просмотр книги в Читай-городе** (UI) — поиск по названию, переход в карточку товара, граничные случаи (пустой запрос, запрос без результатов). Файл: `tests/ui/test_chitai_gorod_search.py`.
2. **CRUD задач в Todo List API** (API, позитивные) — получение списка, получение одной задачи, создание, обновление, удаление. Файл: `tests/api/test_todo_crud.py`.
3. **Негативные сценарии Todo List API** (API) — несуществующий id, невалидный формат id, отсутствие обязательного поля. Файл: `tests/api/test_todo_negative.py`.

Все селекторы и коды ответов подтверждены вручную на живых сайтах перед написанием тестов.

## Стек технологий

- Python 3.10+
- pytest — тест-раннер
- requests — API-тесты
- Playwright — UI-тесты, headless Chromium
- Allure — отчётность

## Структура проекта

```
diploma_automation/
├── config.py                       # базовые URL, генератор тестовых данных
├── conftest.py                     # фикстуры: api_session (requests), browser/page (Playwright)
├── requirements.txt
├── pytest.ini
├── .gitignore
├── tests/
│   ├── api/
│   │   ├── test_todo_crud.py       # 5 позитивных тест-кейсов
│   │   └── test_todo_negative.py   # 3 негативных тест-кейса
│   └── ui/
│       └── test_chitai_gorod_search.py  # 5 UI-тест-кейсов
└── README.md
```

## Установка

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Переменные окружения и авторизация не требуются — оба тестируемых ресурса открыты без входа.

## Запуск тестов

```bash
# все тесты
pytest --alluredir=allure-results

# только API
pytest tests/api -v -m api

# только UI
pytest tests/ui -v -m ui

# отчёт Allure
allure serve allure-results
```

## Статус проверки

Полный набор из 13 тестов реально прогнан локально (23.09.2026): `pytest --alluredir=allure-results` → **13 passed, 0 failed** (11.94 сек, 8 API + 5 UI). Allure-отчёт сгенерирован (`allure generate` + `allure open`) — Overview показывает 100%.

По ходу прогона найден и исправлен баг в UI-тестах: `page.wait_for_load_state("networkidle")` не срабатывал на chitai-gorod.ru из-за фоновых запросов сайта (аналитика/рекомендации) — таймаут 30 сек на 3 из 5 UI-тестов. Заменено на явное ожидание нужного селектора/URL (`wait_for_selector`, `wait_for_url`), после чего все тесты проходят стабильно.

Каждый HTTP-статус и CSS-селектор, использованный в тестах, дополнительно подтверждён вручную живым запросом к реальному сайту/API перед написанием кода.

Postman-коллекция с теми же 8 API-кейсами (5 позитивных + 3 негативных) под новый сервис: [`Todo_List_API_JSONPlaceholder.postman_collection.json`](./Todo_List_API_JSONPlaceholder.postman_collection.json).

## Найденные дефекты

**BR-001** (Low/Minor): контраст текста ценового бейджа скидки (например «-17%») на главной странице chitai-gorod.ru — 4.04:1 при пороге WCAG 2.1 AA 4.5:1 для обычного текста. Белый текст (#FFFFFF) на фоне #E1426C, 12px/500. Не мешает восприятию визуально, но не проходит формальный критерий доступности.
