"""Сборка приложения FastAPI."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import APP_NAME, APP_VERSION

STATIC = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Создать приложение со статической главной страницей."""
    application = FastAPI(
        title=f"{APP_NAME} — API",
        version=APP_VERSION,
        description="Лабораторная работа №6, вариант 7: REST API заметок.",
    )
    application.mount("/static", StaticFiles(directory=STATIC), name="static")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        """Главная — статическая страница."""
        return FileResponse(STATIC / "index.html")

    return application


app = create_app()
