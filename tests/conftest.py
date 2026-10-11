"""Общая фикстура: тестовый клиент приложения."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """Клиент к приложению."""
    return TestClient(create_app())
