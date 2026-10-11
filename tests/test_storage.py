"""Тесты схем и хранилища заметок."""

import pytest
from pydantic import ValidationError

from app.schemas import NoteCreate, NoteUpdate, clean_tags
from app.storage import NoteRepository, demo_repository


def test_clean_tags():
    assert clean_tags([" Дом", "дом", "", "ДАЧА "]) == ["дом", "дача"]
    with pytest.raises(ValueError):
        clean_tags([str(i) for i in range(11)])


def test_schema_strips_and_validates():
    assert NoteCreate(title="  Заголовок ").title == "Заголовок"
    with pytest.raises(ValidationError):
        NoteCreate(title="   ")


def test_create_get_delete():
    repository = NoteRepository()
    note = repository.create(NoteCreate(title="А"))
    assert repository.get(note.id) == note
    assert repository.delete(note.id) is True
    assert repository.get(note.id) is None
    assert repository.delete(note.id) is False


def test_ids_are_not_reused():
    repository = NoteRepository()
    first = repository.create(NoteCreate(title="А"))
    repository.delete(first.id)
    assert repository.create(NoteCreate(title="Б")).id == first.id + 1


def test_update_changes_only_given_fields():
    repository = NoteRepository()
    note = repository.create(NoteCreate(title="А", text="т", tags=["x"]))
    changed = repository.update(note.id, NoteUpdate(text="новый"))
    assert (changed.title, changed.text, changed.tags) == ("А", "новый", ["x"])
    assert changed.created_at == note.created_at
    assert repository.update(999, NoteUpdate(text="x")) is None


def test_list_search_and_tags():
    repository = demo_repository()
    assert [n.id for n in repository.list()] == [3, 2, 1]
    assert [n.id for n in repository.list("REST")] == [3]
    assert [n.id for n in repository.list(tag="УЧЁБА")] == [3, 1]
    assert repository.tags() == ["веб", "дом", "покупки", "учёба"]
    assert repository.count() == 3
