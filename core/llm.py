"""
core/llm.py
-----------
Thin wrapper around the Ollama HTTP API.
No Streamlit dependency — pure Python, fully testable.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from core.config import settings


@dataclass
class GenerationResult:
    sql: str
    success: bool
    error: str | None = None


@dataclass
class HealthResult:
    online: bool
    model_name: str
    message: str


def generate_sql(prompt: str) -> GenerationResult:
    """
    Send a fully-rendered prompt to Ollama and return the SQL response.

    Args:
        prompt: The complete prompt string (already rendered by core.prompt).

    Returns:
        GenerationResult with the SQL text or an error message.
    """
    payload = {
        "model": settings.ollama.model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": settings.ollama.temperature,
            "top_p": settings.ollama.top_p,
        },
    }

    try:
        response = requests.post(
            settings.ollama.url,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        sql = response.json().get("response", "").strip()
        return GenerationResult(sql=sql, success=True)

    except requests.exceptions.Timeout:
        return GenerationResult(sql="", success=False, error="Request timed out (120s).")
    except requests.exceptions.ConnectionError:
        return GenerationResult(sql="", success=False, error="Cannot connect to Ollama server.")
    except requests.exceptions.HTTPError as exc:
        return GenerationResult(sql="", success=False, error=f"HTTP error: {exc}")
    except Exception as exc:  # noqa: BLE001
        return GenerationResult(sql="", success=False, error=str(exc))


def health_check() -> HealthResult:
    """
    Ping the Ollama tags endpoint to verify the server is reachable.

    Returns:
        HealthResult indicating online status and model name.
    """
    try:
        response = requests.get(settings.ollama.tags_url, timeout=4)
        response.raise_for_status()
        return HealthResult(
            online=True,
            model_name=settings.ollama.model_name,
            message="online",
        )
    except Exception:  # noqa: BLE001
        return HealthResult(
            online=False,
            model_name=settings.ollama.model_name,
            message="unreachable",
        )
