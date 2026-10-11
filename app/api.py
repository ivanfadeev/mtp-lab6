"""JSON-эндпоинт со сведениями о приложении."""

from fastapi import APIRouter, Request

from app import APP_NAME, APP_VERSION, AUTHOR, GROUP, VARIANT
from app.schemas import AppInfo
from app.storage import NoteRepository, utc_now

router = APIRouter(prefix="/api")


def repository(request: Request) -> NoteRepository:
    """Хранилище заметок текущего приложения."""
    return request.app.state.notes


@router.get("/info", response_model=AppInfo, tags=["Сведения"])
def info(request: Request) -> AppInfo:
    """Вернуть сведения о приложении в формате JSON."""
    notes = repository(request)
    return AppInfo(
        app=APP_NAME,
        version=APP_VERSION,
        author=AUTHOR,
        group=GROUP,
        variant=VARIANT,
        notes_count=notes.count(),
        tags=notes.tags(),
        server_time=utc_now(),
    )
