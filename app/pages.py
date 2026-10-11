"""HTML-страницы: шаблон Jinja2 со списком заметок и форма добавления."""

from pathlib import Path

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app import APP_NAME, APP_VERSION
from app.schemas import NoteCreate

TEMPLATES = Jinja2Templates(directory=Path(__file__).parent / "templates")
router = APIRouter(include_in_schema=False)


def render_notes(
    request: Request,
    query: str = "",
    tag: str | None = None,
    error: str | None = None,
    form: dict | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    """Отрисовать страницу заметок по шаблону notes.html."""
    notes = request.app.state.notes
    context = {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "notes": notes.list(query, tag),
        "total": notes.count(),
        "tags": notes.tags(),
        "query": query,
        "active_tag": tag,
        "error": error,
        "form": form or {"title": "", "text": "", "tags": ""},
    }
    return TEMPLATES.TemplateResponse(
        request, "notes.html", context, status_code=status_code
    )


@router.get("/notes", response_class=HTMLResponse)
def notes_page(
    request: Request, q: str = "", tag: str | None = None
) -> HTMLResponse:
    """Страница со списком заметок, поиском и формой."""
    return render_notes(request, q, tag)


@router.post("/notes", response_class=HTMLResponse)
def add_note_from_form(
    request: Request,
    title: str = Form(""),
    text: str = Form(""),
    tags: str = Form(""),
) -> HTMLResponse:
    """Обработать отправку формы.

    При успехе — перенаправление 303 обратно на /notes (шаблон
    POST → Redirect → GET, чтобы обновление страницы не отправляло
    форму повторно). При ошибке страница показывается снова с
    сообщением и введёнными данными, статус 400.
    """
    form = {"title": title, "text": text, "tags": tags}
    try:
        data = NoteCreate(title=title, text=text, tags=tags.split(","))
    except ValidationError as error:
        message = "; ".join(
            item["msg"].removeprefix("Value error, ")
            for item in error.errors()
        )
        return render_notes(
            request, error=message, form=form,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.app.state.notes.create(data)
    return RedirectResponse("/notes", status_code=status.HTTP_303_SEE_OTHER)
