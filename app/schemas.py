"""Схемы данных API заметок (Pydantic)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_TAGS = 10


def clean_tags(tags: list[str]) -> list[str]:
    """Привести теги к нижнему регистру, убрать пустые и повторы.

    Порядок первого появления сохраняется. Больше MAX_TAGS тегов
    указывать нельзя.
    """
    result: list[str] = []
    for tag in tags:
        value = tag.strip().lower()
        if value and value not in result:
            result.append(value)
    if len(result) > MAX_TAGS:
        raise ValueError(f"не больше {MAX_TAGS} тегов")
    return result


class NoteBase(BaseModel):
    """Общие поля заметки."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100, examples=["Купить"])
    text: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list, examples=[["дом"]])

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, tags: list[str]) -> list[str]:
        """Нормализовать список тегов."""
        return clean_tags(tags)


class NoteCreate(NoteBase):
    """Данные для создания заметки и полной замены (PUT)."""


class NoteUpdate(BaseModel):
    """Частичное изменение заметки (PATCH): все поля необязательны."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=100)
    text: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = None

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, tags: list[str] | None) -> list[str] | None:
        """Нормализовать список тегов, если он передан."""
        return None if tags is None else clean_tags(tags)


class Note(BaseModel):
    """Заметка в том виде, в каком её возвращает API."""

    id: int
    title: str
    text: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class AppInfo(BaseModel):
    """Сведения о приложении для эндпоинта /api/info."""

    app: str
    version: str
    author: str
    group: str
    variant: int
    notes_count: int
    tags: list[str]
    server_time: datetime
