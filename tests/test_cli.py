import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from feedlens.cli import app
from feedlens.config import get_settings

runner = CliRunner()


@pytest.fixture(autouse=True)
def _home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("FEEDLENS_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("FEEDLENS_DECISION_BACKEND", "fake")
    get_settings.cache_clear()
    yield tmp_path / "home"
    get_settings.cache_clear()


def test_init_creates_db_and_applies_migrations(_home: Path) -> None:
    r = runner.invoke(app, ["init"])
    assert r.exit_code == 0, r.output
    assert (_home / "feedlens.db").exists()
    assert "feedlens.db" in r.output and "1" in r.output
    r2 = runner.invoke(app, ["init"])
    assert r2.exit_code == 0 and "up to date" in r2.output


def test_decide_adhoc_prints_all_questions(_home: Path) -> None:
    r = runner.invoke(
        app,
        ["decide", "--backend", "fake", "--title", "Rust async deep dive", "--text", "tokio"],
    )
    assert r.exit_code == 0, r.output
    for q in ("topics", "fit", "depth", "clickbait", "novelty", "avoid"):
        assert q in r.output
    assert "fake" in r.output  # backend id shown


def test_decide_item_from_db(_home: Path) -> None:
    assert runner.invoke(app, ["init"]).exit_code == 0
    conn = sqlite3.connect(_home / "feedlens.db")
    conn.execute(
        "insert into items(id,url_hash,kind,url,title,text,created_at) values (?,?,?,?,?,?,?)",
        ("i1", "h1", "video", "https://y/1", "Some video", "desc", "c"),
    )
    conn.commit()
    r = runner.invoke(app, ["decide", "--item", "i1"])
    assert r.exit_code == 0, r.output
    assert "Some video" in r.output and "clickbait" in r.output
    r2 = runner.invoke(app, ["decide", "--item", "nope"])
    assert r2.exit_code == 1 and "not found" in r2.output


def test_decide_requires_item_or_title() -> None:
    r = runner.invoke(app, ["decide"])
    assert r.exit_code == 2


def test_stats_on_empty_db(_home: Path) -> None:
    r = runner.invoke(app, ["stats"])
    assert r.exit_code == 0, r.output
    assert "items: 0" in r.output
    assert "signals: 0" in r.output
    assert "decisions: 0" in r.output


def test_decide_rejects_unknown_backend() -> None:
    r = runner.invoke(app, ["decide", "--backend", "bogus", "--title", "x"])
    assert r.exit_code == 2
    assert "Traceback" not in r.output
    assert "bogus" in r.output


def test_decide_unimplemented_backend_is_a_clean_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEEDLENS_DECISION_BACKEND", "ollama")
    get_settings.cache_clear()
    r = runner.invoke(app, ["decide", "--title", "x"])
    assert r.exit_code == 2
    assert "Traceback" not in r.output
    assert "not implemented" in r.output and "--backend fake" in r.output
