"""Settings (task T-0.2).

All knobs are `FEEDLENS_*` environment variables (or `.env`); data lives under `~/.feedlens`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEEDLENS_", env_file=".env", extra="ignore")

    home: Path = Path("~/.feedlens")
    host: str = "127.0.0.1"
    port: int = 8765
    decision_backend: Literal["ollama", "typesafe", "fake"] = "ollama"
    ollama_url: str = "http://127.0.0.1:11434"
    decision_model: str = "qwen3.5:4b"
    decision_concurrency: int = 4
    question_set_version: str = "v1"
    max_state_tokens: int = 4000
    embed_model: str = "qwen3-embedding:0.6b"
    embed_dim: int = 1024
    refresh_interval_min: int = 15
    scheduler: Literal["on", "off"] = "on"
    pool_k: int = 200

    @property
    def home_dir(self) -> Path:
        return self.home.expanduser()

    @property
    def db_path(self) -> Path:
        return self.home_dir / "feedlens.db"


def ensure_home(settings: Settings) -> Path:
    """Create the data directory (private to the user) and return it."""
    home = settings.home_dir
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    home.chmod(0o700)
    return home


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings; call `get_settings.cache_clear()` in tests."""
    return Settings()
