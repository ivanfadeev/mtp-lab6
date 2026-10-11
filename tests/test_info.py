"""Тесты JSON-эндпоинта /api/info."""

from datetime import datetime

from app.schemas import NoteCreate


def test_info_returns_json(demo_client):
    response = demo_client.get("/api/info")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["variant"] == 7
    assert data["group"] == "221141"
    assert data["notes_count"] == 3
    assert data["tags"] == ["веб", "дом", "покупки", "учёба"]
    assert datetime.fromisoformat(data["server_time"]).tzinfo is not None


def test_info_follows_changes(client):
    client.app.state.notes.create(NoteCreate(title="А", tags=["x"]))
    data = client.get("/api/info").json()
    assert (data["notes_count"], data["tags"]) == (1, ["x"])


def test_info_is_documented_in_openapi(client):
    schema = client.get("/openapi.json").json()
    assert "/api/info" in schema["paths"]
