"""
core/storage.py
---------------
Persists named prompt templates to a local JSON file.
No Streamlit dependency — pure Python, fully testable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from core.config import settings
from core.prompt import DEFAULT_TEMPLATE

_PROMPTS_FILE: Path = settings.prompts_file


@dataclass
class PromptTemplate:
    name: str
    template: str
    active: bool = False


def _read_file() -> list[PromptTemplate]:
    if not _PROMPTS_FILE.exists():
        return []
    try:
        raw = json.loads(_PROMPTS_FILE.read_text(encoding="utf-8"))
        return [PromptTemplate(**item) for item in raw]
    except (json.JSONDecodeError, TypeError):
        return []


def _write_file(templates: list[PromptTemplate]) -> None:
    _PROMPTS_FILE.write_text(
        json.dumps([asdict(t) for t in templates], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def list_templates() -> list[PromptTemplate]:
    """Return all saved prompt templates."""
    return _read_file()


def get_active_template() -> PromptTemplate:
    """
    Return the currently active template.
    Falls back to the built-in default if none is saved or marked active.
    """
    templates = _read_file()
    for t in templates:
        if t.active:
            return t
    return PromptTemplate(name="Default", template=DEFAULT_TEMPLATE, active=True)


def save_template(name: str, template: str) -> PromptTemplate:
    """
    Create or update a template by name.
    Does NOT change the active flag.
    """
    templates = _read_file()
    for existing in templates:
        if existing.name == name:
            existing.template = template
            _write_file(templates)
            return existing

    new = PromptTemplate(name=name, template=template, active=False)
    templates.append(new)
    _write_file(templates)
    return new


def set_active_template(name: str) -> bool:
    """
    Mark a template as active (deactivates all others).

    Returns:
        True if the template was found and activated, False otherwise.
    """
    templates = _read_file()
    found = False
    for t in templates:
        t.active = t.name == name
        if t.active:
            found = True
    if found:
        _write_file(templates)
    return found


def delete_template(name: str) -> bool:
    """
    Delete a template by name.

    Returns:
        True if deleted, False if not found.
    """
    templates = _read_file()
    filtered = [t for t in templates if t.name != name]
    if len(filtered) == len(templates):
        return False
    _write_file(filtered)
    return True
