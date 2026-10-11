"""Тесты статической страницы и CSS."""


def test_index_is_static_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<link rel="stylesheet" href="/static/style.css">' in response.text


def test_stylesheet_is_served(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert ".card" in response.text


def test_missing_static_file(client):
    assert client.get("/static/nope.css").status_code == 404
