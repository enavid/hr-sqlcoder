"""
core/config.py
--------------
Single source of truth for all application settings.
Reads from .env via python-dotenv and exposes a typed Settings instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class OllamaSettings:
    url: str
    tags_url: str
    model_name: str
    temperature: float
    top_p: float


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


@dataclass(frozen=True)
class AppSettings:
    ollama: OllamaSettings
    database: DatabaseSettings
    schema_path: Path
    prompts_file: Path = field(default=Path("prompts.json"))


def _load_settings() -> AppSettings:
    return AppSettings(
        ollama=OllamaSettings(
            url=os.environ["OLLAMA_URL"],
            tags_url=os.environ["OLLAMA_TAGS_URL"],
            model_name=os.environ["MODEL_NAME"],
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.4")),
            top_p=float(os.getenv("MODEL_TOP_P", "0.5")),
        ),
        database=DatabaseSettings(
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        ),
        schema_path=Path(os.getenv("SCHEMA_PATH", "./schema_context.txt")),
    )


settings: AppSettings = _load_settings()
