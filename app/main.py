"""Сборка приложения FastAPI."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import APP_NAME, APP_VERSION, api, pages
from app.storage import NoteRepository, demo_repository

STATIC = Path(__file__).parent / "static"


def create_app(notes: NoteRepository | None = None) -> FastAPI:
    """Создать приложение; без аргумента — с демонстрационными заметками.

    Хранилище кладётся в app.state, поэтому тесты передают своё.
    """
    application = FastAPI(
        title=f"{APP_NAME} — API",
        version=APP_VERSION,
        description="Лабораторная работа №6, вариант 7: REST API заметок.",
    )
    application.state.notes = notes if notes is not None else (
        demo_repository()
    )
    application.mount("/static", StaticFiles(directory=STATIC), name="static")
    application.include_router(api.router)
    application.include_router(pages.router)

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        """Главная — статическая страница."""
        return FileResponse(STATIC / "index.html")

    return application


app = create_app()
