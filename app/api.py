"""REST API заметок и JSON-эндпоинт со сведениями о приложении."""

from fastapi import APIRouter, HTTPException, Query, Request, Response, status

from app import APP_NAME, APP_VERSION, AUTHOR, GROUP, VARIANT
from app.schemas import AppInfo, Note, NoteCreate, NoteUpdate
from app.storage import NoteRepository, utc_now

router = APIRouter(prefix="/api")


def repository(request: Request) -> NoteRepository:
    """Хранилище заметок текущего приложения."""
    return request.app.state.notes


def or_404(note: Note | None) -> Note:
    """Вернуть заметку или ответить 404, если её нет."""
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "заметка не найдена")
    return note


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


@router.get("/notes", response_model=list[Note], tags=["Заметки"])
def list_notes(
    request: Request,
    q: str = Query("", max_length=100, description="поиск по тексту"),
    tag: str | None = Query(None, description="фильтр по тегу"),
) -> list[Note]:
    """Список заметок (новые сверху) с поиском и фильтром по тегу."""
    return repository(request).list(q, tag)


@router.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["Заметки"],
)
def create_note(
    request: Request, data: NoteCreate, response: Response
) -> Note:
    """Создать заметку; адрес новой заметки — в заголовке Location."""
    note = repository(request).create(data)
    response.headers["Location"] = f"/api/notes/{note.id}"
    return note


@router.get("/notes/{note_id}", response_model=Note, tags=["Заметки"])
def read_note(request: Request, note_id: int) -> Note:
    """Получить одну заметку."""
    return or_404(repository(request).get(note_id))


@router.put("/notes/{note_id}", response_model=Note, tags=["Заметки"])
def replace_note(request: Request, note_id: int, data: NoteCreate) -> Note:
    """Полностью заменить заметку."""
    return or_404(repository(request).replace(note_id, data))


@router.patch("/notes/{note_id}", response_model=Note, tags=["Заметки"])
def update_note(request: Request, note_id: int, data: NoteUpdate) -> Note:
    """Изменить отдельные поля заметки."""
    return or_404(repository(request).update(note_id, data))


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Заметки"],
)
def delete_note(request: Request, note_id: int) -> Response:
    """Удалить заметку."""
    if not repository(request).delete(note_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "заметка не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
