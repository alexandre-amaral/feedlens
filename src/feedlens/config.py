"""Settings (task T-0.2)."""

from __future__ import annotations

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
