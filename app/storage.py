"""Хранилище заметок в памяти."""

import threading
from datetime import datetime, timezone

from app.schemas import Note, NoteCreate, NoteUpdate


def utc_now() -> datetime:
    """Текущее время в UTC без микросекунд."""
    return datetime.now(timezone.utc).replace(microsecond=0)


class NoteRepository:
    """Заметки в памяти процесса с автоматическим id.

    Данные живут, пока работает сервер, — на Heroku это до
    перезапуска dyno, поэтому для учебного приложения база не нужна.
    Операции защищены блокировкой, так как сервер может обрабатывать
    запросы в нескольких потоках.
    """

    def __init__(self) -> None:
        self._notes: dict[int, Note] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def list(self, query: str = "", tag: str | None = None) -> list[Note]:
        """Заметки, новые сверху, с фильтром по тексту и тегу.

        query ищется без учёта регистра в заголовке и тексте.
        """
        needle = query.strip().casefold()
        with self._lock:
            notes = list(self._notes.values())
        if needle:
            notes = [
                note for note in notes
                if needle in note.title.casefold()
                or needle in note.text.casefold()
            ]
        if tag:
            notes = [note for note in notes if tag.lower() in note.tags]
        return sorted(notes, key=lambda note: note.id, reverse=True)

    def get(self, note_id: int) -> Note | None:
        """Заметка по id или None."""
        with self._lock:
            return self._notes.get(note_id)

    def create(self, data: NoteCreate) -> Note:
        """Создать заметку и вернуть её."""
        with self._lock:
            now = utc_now()
            note = Note(
                id=self._next_id, created_at=now, updated_at=now,
                **data.model_dump(),
            )
            self._notes[note.id] = note
            self._next_id += 1
            return note

    def replace(self, note_id: int, data: NoteCreate) -> Note | None:
        """Полностью заменить заметку; None, если её нет."""
        return self._change(note_id, data.model_dump())

    def update(self, note_id: int, data: NoteUpdate) -> Note | None:
        """Изменить переданные поля заметки; None, если её нет."""
        return self._change(note_id, data.model_dump(exclude_none=True))

    def delete(self, note_id: int) -> bool:
        """Удалить заметку; False, если её не было."""
        with self._lock:
            return self._notes.pop(note_id, None) is not None

    def tags(self) -> list[str]:
        """Все теги заметок по алфавиту."""
        with self._lock:
            notes = list(self._notes.values())
        return sorted({tag for note in notes for tag in note.tags})

    def count(self) -> int:
        """Количество заметок."""
        with self._lock:
            return len(self._notes)

    def _change(self, note_id: int, fields: dict) -> Note | None:
        """Записать новые значения полей и обновить updated_at."""
        with self._lock:
            note = self._notes.get(note_id)
            if note is None:
                return None
            changed = note.model_copy(
                update={**fields, "updated_at": utc_now()}
            )
            self._notes[note_id] = changed
            return changed


def demo_repository() -> NoteRepository:
    """Хранилище с несколькими заметками для первого запуска."""
    repository = NoteRepository()
    samples = [
        ("Подготовить отчёт по ЛР №6", "Скриншоты, ссылки, вывод тестов",
         ["учёба"]),
        ("Купить продукты", "Молоко, хлеб, яблоки", ["дом", "покупки"]),
        ("Прочитать про REST", "Методы HTTP и коды ответов",
         ["учёба", "веб"]),
    ]
    for title, text, tags in samples:
        repository.create(NoteCreate(title=title, text=text, tags=tags))
    return repository
