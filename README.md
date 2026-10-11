# Лабораторная работа №6 — веб-программирование

**Фадеев Иван Александрович, группа 221141, вариант 7, лабораторная №6**

Дисциплина: «Методы и технологии программирования» (часть 1).

## Задания варианта 7

| № | Сложность | Задание из общего списка | Где в коде |
|---|-----------|--------------------------|------------|
| 1 | средняя | 7. FastAPI endpoint возвращает JSON | `app/api.py` — `GET /api/info` |
| 2 | средняя | 9. Шаблон Jinja2 с данными | `app/pages.py`, `app/templates/notes.html` — `GET /notes` |
| 3 | средняя | 3. Статическая страница + CSS | `app/static/index.html`, `app/static/style.css` — `GET /` |
| 4 | повышенная | 7. Деплой на Heroku | `Procfile`, `.python-version`, `requirements.txt` |
| 5 | повышенная | 5. REST API для заметок | `app/api.py` — `/api/notes` |

Все задания — части одного приложения «Заметки»: статическая главная
страница, HTML-страница со списком заметок на шаблоне Jinja2, REST API
с документацией Swagger и JSON-эндпоинт со сведениями о приложении.

## Темы из методички

| Тема | Как применена |
|------|---------------|
| FastAPI, создание маршрутов | маршруты в двух `APIRouter` (`app/api.py` — API, `app/pages.py` — HTML), сборка в `create_app()` |
| Обработка GET и POST | `GET /notes` показывает страницу, `POST /notes` принимает HTML-форму (`Form(...)`) и отвечает перенаправлением 303 |
| Шаблоны Jinja2 | `base.html` с блоками и `notes.html`, наследующий его (`extends`), циклы `for … else`, условия, фильтры `length` и `urlencode`, `url_for` для статики, автоэкранирование HTML |
| REST API | ресурс `/api/notes`: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, коды 200/201/204/404/422, заголовок `Location` |
| Документация Swagger | генерируется автоматически по схемам Pydantic: `/docs`, `/openapi.json` |

Все задания варианта решаются средствами FastAPI: шаблоны Jinja2 и
статические файлы он поддерживает сам, поэтому второй фреймворк (Flask)
в проекте не нужен.

## Структура проекта

```
app/__init__.py          название, версия, автор
app/main.py              create_app(): статика, роутеры, главная страница
app/schemas.py           схемы Pydantic: NoteCreate, NoteUpdate, Note, AppInfo
app/storage.py           NoteRepository — заметки в памяти
app/api.py               REST API заметок и GET /api/info
app/pages.py             страница /notes на шаблоне и обработка формы
app/templates/           base.html, notes.html — шаблоны Jinja2
app/static/              index.html и style.css — статическая страница
Procfile                 команда запуска на Heroku
.python-version          версия Python для Heroku
requirements.txt         зависимости с точными версиями
tests/                   тесты pytest (TestClient)
```

## Адреса

| Метод и адрес | Что делает |
|---------------|------------|
| `GET /` | статическая страница `index.html` со стилями `style.css` |
| `GET /notes?q=&tag=` | страница заметок на шаблоне Jinja2: список, поиск, теги, форма |
| `POST /notes` | добавление заметки из HTML-формы, ответ 303 → `/notes` |
| `GET /api/info` | JSON со сведениями о приложении |
| `GET /api/notes?q=&tag=` | список заметок (новые сверху) с поиском и фильтром |
| `POST /api/notes` | создать заметку → 201 и заголовок `Location` |
| `GET /api/notes/{id}` | получить заметку или 404 |
| `PUT /api/notes/{id}` | заменить заметку целиком |
| `PATCH /api/notes/{id}` | изменить отдельные поля |
| `DELETE /api/notes/{id}` | удалить заметку → 204 |
| `GET /docs` | документация Swagger UI |

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

При старте приложение содержит три демонстрационные заметки. Данные
хранятся в памяти процесса и сбрасываются при перезапуске.

## Отчёт о выполнении

### Задание 3 (средней сложности): статическая страница + CSS

`app/static/index.html` — обычный HTML без шаблонизатора, стили — в
отдельном файле `app/static/style.css` (CSS-переменные, сетка `grid`
для карточек, градиентный заголовок, адаптивная вёрстка). FastAPI
раздаёт папку через `StaticFiles` по адресу `/static`, а `GET /`
возвращает `index.html`. Тот же файл стилей подключают и шаблоны.

### Задание 7 (средней сложности): FastAPI endpoint возвращает JSON

`GET /api/info` возвращает модель Pydantic `AppInfo` — FastAPI сам
превращает её в JSON и описывает схему ответа в Swagger. В ответе
название и версия приложения, автор, группа, вариант, текущее число
заметок, список тегов и время сервера в UTC.

### Задание 9 (средней сложности): шаблон Jinja2 с данными

`GET /notes` передаёт в шаблон `notes.html` данные из хранилища:
заметки, общее число, все теги, строку поиска и выбранный тег.
Шаблон наследует `base.html` (шапка, подключение CSS, подвал) и
выводит карточки в цикле `for … else` («Заметок не найдено.»), облако
тегов со ссылками-фильтрами и форму добавления. Jinja2 экранирует
HTML: заметка с заголовком `<script>` выводится как текст (это
проверяет тест `test_template_escapes_html`).

Форма отправляется методом POST. При успехе сервер отвечает
перенаправлением 303 на `/notes` (шаблон POST → Redirect → GET, чтобы
обновление страницы не отправляло форму повторно), при ошибке
показывает страницу снова с сообщением и введёнными данными:

```console
$ curl -s -X POST http://127.0.0.1:5077/notes -d 'title=Из формы' -d 'tags=дом, сад' -o /dev/null -w '%{http_code} → %{redirect_url}'
303 → http://127.0.0.1:5077/notes
$ curl -s http://127.0.0.1:5077/notes | grep -A3 'class="card"' | head -4   # новая заметка сверху
<article class="card">
  <h2>Из формы</h2>
  
  <p class="meta">
```

### Задание 5 (повышенной сложности): REST API для заметок

Ресурс `/api/notes` поддерживает полный набор операций CRUD.
Входные данные проверяют схемы Pydantic: заголовок от 1 до 100
символов (пробелы по краям обрезаются), текст до 5000 символов, до 10
тегов — теги приводятся к нижнему регистру, пустые и повторы
удаляются. Ошибки возвращаются стандартными кодами: 404 для
несуществующей заметки, 422 для неверных данных. Хранилище защищено
блокировкой, потому что сервер может обрабатывать запросы в
нескольких потоках.

Сеанс работы с API (сервер запущен командой из `Procfile`):

```console
$ curl -s http://127.0.0.1:5077/api/info
{
    "app": "Заметки",
    "version": "1.0.0",
    "author": "Фадеев Иван Александрович",
    "group": "221141",
    "variant": 7,
    "notes_count": 3,
    "tags": [
        "веб",
        "дом",
        "покупки",
        "учёба"
    ],
    "server_time": "2026-10-11T09:49:48Z"
}

$ curl -i -X POST http://127.0.0.1:5077/api/notes -H 'Content-Type: application/json' \
       -d '{"title": "Сдать ЛР №6", "text": "до 25.11", "tags": ["Учёба"]}'
HTTP/1.1 201 Created
location: /api/notes/4
{
    "id": 4,
    "title": "Сдать ЛР №6",
    "text": "до 25.11",
    "tags": [
        "учёба"
    ],
    "created_at": "2026-10-11T09:49:48Z",
    "updated_at": "2026-10-11T09:49:48Z"
}

$ curl -s -X PATCH http://127.0.0.1:5077/api/notes/4 -H 'Content-Type: application/json' -d '{"tags": ["учёба", "срочно"]}'
{
    "id": 4,
    "title": "Сдать ЛР №6",
    "text": "до 25.11",
    "tags": [
        "учёба",
        "срочно"
    ],
    "created_at": "2026-10-11T09:49:48Z",
    "updated_at": "2026-10-11T09:49:48Z"
}

$ curl -s -G http://127.0.0.1:5077/api/notes --data-urlencode 'tag=учёба'   # id и заголовки
4 Сдать ЛР №6 ['учёба', 'срочно']
3 Прочитать про REST ['учёба', 'веб']
1 Подготовить отчёт по ЛР №6 ['учёба']

$ curl -s -o /dev/null -w '%{http_code}' -X DELETE http://127.0.0.1:5077/api/notes/4
204

$ curl -s http://127.0.0.1:5077/api/notes/4
{"detail":"заметка не найдена"}

$ curl -s -X POST http://127.0.0.1:5077/api/notes -H 'Content-Type: application/json' -d '{"title": ""}'
(HTTP 422) ['body', 'title'] String should have at least 1 character
```

Документация Swagger доступна по адресу `/docs`.

### Задание 7 (повышенной сложности): деплой на Heroku

Для Heroku подготовлены три файла:

- `Procfile` — команда веб-процесса. Heroku передаёт порт в переменной
  `PORT`, а сервер должен слушать все интерфейсы:

  ```
  web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

- `.python-version` — версия Python для сборки: `3.14`;
- `requirements.txt` — зависимости с точными версиями, чтобы сборка
  на Heroku совпадала с проверенной локально:

  ```
  fastapi==0.143.0
  uvicorn==0.54.0
  jinja2==3.1.6
  python-multipart==0.0.32
  ```

Развёртывание через Heroku CLI:

```bash
heroku login
heroku create mtp-lab6-fadeev
git push heroku main
heroku open
```

или через панель управления: *New → Create new app → Deploy → GitHub*,
подключить репозиторий `ivanfadeev/mtp-lab6` и нажать *Deploy Branch*.

Проверка, что команда из `Procfile` запускает приложение (локально
вместо `0.0.0.0` использован `127.0.0.1`, порт задан через `PORT`):

```console
$ PORT=5077 uvicorn app.main:app --host 127.0.0.1 --port $PORT
INFO:     Started server process [35502]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5077 (Press CTRL+C to quit)
GET /                  → 200 text/html; charset=utf-8
GET /static/style.css  → 200 text/css; charset=utf-8
GET /notes             → 200 text/html; charset=utf-8
GET /docs              → 200 text/html; charset=utf-8
GET /api/info          → 200 application/json
GET /openapi.json      → 200 application/json
```

Тест `tests/test_heroku.py` проверяет, что `Procfile` ссылается на
существующий объект приложения, версия Python указана, а все
зависимости закреплены.

## Тесты

Тесты обращаются к приложению через `TestClient` без запуска сервера;
каждый тест получает своё хранилище, поэтому они не влияют друг на
друга.

```console
$ pip install -r requirements-dev.txt
$ python -m pytest -q
...................................                                      [100%]
35 passed in 0.11s
```

| Файл | Тестов |
|------|--------|
| `test_heroku.py` | 3 |
| `test_info.py` | 3 |
| `test_notes_api.py` | 15 |
| `test_pages.py` | 5 |
| `test_static.py` | 3 |
| `test_storage.py` | 6 |
