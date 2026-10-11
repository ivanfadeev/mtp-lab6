"""Тесты REST API заметок."""

import pytest


def create(client, **fields):
    payload = {"title": "Заметка", **fields}
    response = client.post("/api/notes", json=payload)
    assert response.status_code == 201
    return response


def test_create_returns_note_and_location(client):
    response = create(client, text="текст", tags=[" Дом ", "дом", "ДАЧА"])
    note = response.json()
    assert note["id"] == 1
    assert note["tags"] == ["дом", "дача"]
    assert note["created_at"] == note["updated_at"]
    assert response.headers["location"] == "/api/notes/1"


def test_list_newest_first_with_filters(client):
    create(client, title="Купить хлеб", tags=["дом"])
    create(client, title="Сдать ЛР", text="хлебные крошки", tags=["учёба"])
    create(client, title="Позвонить")
    titles = [n["title"] for n in client.get("/api/notes").json()]
    assert titles == ["Позвонить", "Сдать ЛР", "Купить хлеб"]
    found = client.get("/api/notes", params={"q": "ХЛЕБ"}).json()
    assert [n["id"] for n in found] == [2, 1]
    tagged = client.get("/api/notes", params={"tag": "учёба"}).json()
    assert [n["id"] for n in tagged] == [2]


def test_read_one_and_404(client):
    create(client)
    assert client.get("/api/notes/1").json()["title"] == "Заметка"
    response = client.get("/api/notes/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "заметка не найдена"}


def test_put_replaces_all_fields(client):
    create(client, text="старый", tags=["a"])
    response = client.put("/api/notes/1", json={"title": "Новая"})
    note = response.json()
    assert (note["title"], note["text"], note["tags"]) == ("Новая", "", [])


def test_patch_changes_only_given_fields(client):
    create(client, text="текст", tags=["a"])
    note = client.patch("/api/notes/1", json={"tags": ["b"]}).json()
    assert (note["title"], note["text"], note["tags"]) == (
        "Заметка", "текст", ["b"],
    )


def test_delete(client):
    create(client)
    assert client.delete("/api/notes/1").status_code == 204
    assert client.delete("/api/notes/1").status_code == 404
    assert client.get("/api/notes").json() == []


@pytest.mark.parametrize("method", ["put", "patch"])
def test_change_missing_note(client, method):
    response = getattr(client, method)("/api/notes/5", json={"title": "x"})
    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "   "},
        {"title": "x" * 101},
        {"title": "ok", "tags": [str(i) for i in range(11)]},
        {"title": "ok", "text": "x" * 5001},
    ],
)
def test_validation_errors(client, payload):
    assert client.post("/api/notes", json=payload).status_code == 422
    assert client.get("/api/notes").json() == []


def test_id_must_be_integer(client):
    assert client.get("/api/notes/abc").status_code == 422


def test_swagger_docs_available(client):
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert set(paths["/api/notes/{note_id}"]) == {
        "get", "put", "patch", "delete",
    }
