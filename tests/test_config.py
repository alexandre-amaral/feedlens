from pathlib import Path

import pytest

from feedlens.config import Settings, ensure_home, get_settings


def test_env_overrides_and_prefix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FEEDLENS_HOME", str(tmp_path / "fl"))
    monkeypatch.setenv("FEEDLENS_PORT", "9999")
    s = Settings()
    assert s.port == 9999
    assert s.home_dir == tmp_path / "fl"
    assert s.db_path == tmp_path / "fl" / "feedlens.db"


def test_home_expands_user() -> None:
    s = Settings(home=Path("~/.feedlens"))
    assert not str(s.home_dir).startswith("~")
    assert s.home_dir.is_absolute()


def test_phase0_defaults() -> None:
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.decision_backend == "ollama"
    assert s.decision_concurrency == 4
    assert s.question_set_version == "v1"
    assert s.max_state_tokens == 4000
    assert s.embed_dim == 1024


def test_ensure_home_creates_private_dir(tmp_path: Path) -> None:
    s = Settings(home=tmp_path / "home" / ".feedlens")
    created = ensure_home(s)
    assert created == s.home_dir
    assert created.is_dir()
    assert (created.stat().st_mode & 0o777) == 0o700


def test_get_settings_is_cached_and_clearable(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("FEEDLENS_PORT", "8001")
    a = get_settings()
    monkeypatch.setenv("FEEDLENS_PORT", "8002")
    assert get_settings() is a  # cached
    get_settings.cache_clear()
    assert get_settings().port == 8002
