"""Проверка конфигурации развёртывания на Heroku."""

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_procfile_points_to_application():
    line = (ROOT / "Procfile").read_text(encoding="utf-8").strip()
    match = re.fullmatch(
        r"web: uvicorn (\S+):(\w+) --host 0\.0\.0\.0 --port \$PORT", line
    )
    assert match, line
    module = importlib.import_module(match.group(1))
    assert hasattr(getattr(module, match.group(2)), "routes")


def test_python_version_is_pinned():
    version = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"3\.\d+", version)


def test_runtime_requirements_are_pinned():
    lines = (ROOT / "requirements.txt").read_text(encoding="utf-8").split()
    names = {line.split("==")[0] for line in lines}
    assert {"fastapi", "uvicorn", "jinja2", "python-multipart"} <= names
    assert all("==" in line for line in lines)
