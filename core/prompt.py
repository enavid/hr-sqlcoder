"""
core/prompt.py
--------------
Handles prompt construction and schema loading.
No Streamlit dependency — pure Python, fully testable.
"""

from __future__ import annotations

from pathlib import Path

from core.config import settings


def load_schema() -> str:
    """Read schema context from the path defined in settings."""
    path: Path = settings.schema_path
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return path.read_text(encoding="utf-8")


def build_prompt(question: str, template: str) -> str:
    """
    Render the prompt template by injecting the schema and question.

    The template must contain two placeholders:
        {schema_context}  — replaced with the contents of schema_context.txt
        {question}        — replaced with the user's question
    """
    schema = load_schema()
    return template.replace("{schema_context}", schema).replace("{question}", question)


DEFAULT_TEMPLATE: str = """\
You are a PostgreSQL SQL generator specialized in HR analytics.

TASK:
Generate exactly ONE valid PostgreSQL SELECT query.

IMPORTANT RULES:
- Return ONLY SQL.
- Do NOT explain anything.
- Do NOT use markdown or code fences.
- Do NOT generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Use only the provided tables and columns.
- Always use schema prefix: hr_mvp.
- Always use table aliases.
- Always use explicit JOIN conditions.

FILTERS (always apply):
- Active employees : e.is_active = TRUE
- Current contract : c.is_current = TRUE
- Latest education : ee.is_latest = TRUE

AGGREGATION RULES:
- For employee counts use: COUNT(e.employee_id)
- If question contains gender keywords → GROUP BY e.gender
- If question asks for "most" / max  → ORDER BY ... DESC LIMIT 1
- If question asks for "least" / min → ORDER BY ... ASC  LIMIT 1
- If question asks for percentage    → ROUND(... * 100.0 / ..., 2)

DATABASE: PostgreSQL
SCHEMA: hr_mvp

SCHEMA CONTEXT:
{schema_context}

QUESTION:
{question}

SQL:"""
