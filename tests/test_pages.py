"""Тесты страницы на шаблоне Jinja2 и формы."""

from app.schemas import NoteCreate


def test_template_renders_notes(demo_client):
    response = demo_client.get("/notes")
    assert response.status_code == 200
    page = response.text
    assert "Показано 3 из 3" in page
    assert "Купить продукты" in page
    assert 'href="/notes?tag=%D1%83%D1%87%D1%91%D0%B1%D0%B0"' in page
    assert '<link rel="stylesheet"' in page


def test_template_search_and_tag(demo_client):
    page = demo_client.get("/notes", params={"tag": "учёба"}).text
    assert "Показано 2 из 3" in page
    assert "Купить продукты" not in page
    page = demo_client.get("/notes", params={"q": "нет такого"}).text
    assert "Заметок не найдено." in page


def test_template_escapes_html(client):
    client.app.state.notes.create(
        NoteCreate(title="<script>alert(1)</script>")
    )
    page = client.get("/notes").text
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_form_post_redirects_and_adds(client):
    response = client.post(
        "/notes",
        data={"title": "Из формы", "text": "текст", "tags": "a, b"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/notes"
    note = client.app.state.notes.list()[0]
    assert (note.title, note.tags) == ("Из формы", ["a", "b"])


def test_form_error_keeps_input(client):
    response = client.post("/notes", data={"title": " ", "text": "черновик"})
    assert response.status_code == 400
    assert "Ошибка:" in response.text
    assert "черновик" in response.text
    assert client.app.state.notes.count() == 0
