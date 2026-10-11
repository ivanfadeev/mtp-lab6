"""Общие фикстуры: приложение с пустым и демонстрационным хранилищем."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.storage import NoteRepository, demo_repository


@pytest.fixture
def client():
    """Клиент к приложению с пустым хранилищем."""
    return TestClient(create_app(NoteRepository()))


@pytest.fixture
def demo_client():
    """Клиент к приложению с демонстрационными заметками."""
    return TestClient(create_app(demo_repository()))
