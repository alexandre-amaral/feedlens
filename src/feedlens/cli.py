"""CLI (task T-0.7): `init`, `decide`, `stats`; `serve`/`refresh` land in Phase 2."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from typing import Annotated

import typer

from feedlens.config import Settings, ensure_home, get_settings
from feedlens.decisions.cache import DecisionCache
from feedlens.decisions.contract import Answer, ChoiceAnswer, NoulAnswer, ScoreAnswer
from feedlens.decisions.questions import get_question_set
from feedlens.decisions.registry import get_backend
from feedlens.decisions.state import render_state
from feedlens.models import Item, ItemKind, Profile
from feedlens.store.db import connect, migrate

app = typer.Typer(help="feedlens — your feed, your algorithm.", no_args_is_help=True)


def _open(settings: Settings) -> sqlite3.Connection:
    ensure_home(settings)
    conn = connect(settings.db_path)
    migrate(conn)
    return conn


def _load_profile(conn: sqlite3.Connection) -> Profile:
    row = conn.execute(
        "SELECT text, topics, avoid, depth_pref FROM profile WHERE id = 1"
    ).fetchone()
    if row is None:
        return Profile()
    return Profile(
        text=row["text"],
        topics=json.loads(row["topics"]),
        avoid=json.loads(row["avoid"]),
        depth_pref=row["depth_pref"],
    )


def _load_item(conn: sqlite3.Connection, item_id: str) -> Item | None:
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["metadata"] = json.loads(data.get("metadata") or "{}")
    return Item.model_validate(data)


def _format_answer(a: Answer) -> str:
    if isinstance(a, NoulAnswer):
        return f"p={a.p:.2f}"
    if isinstance(a, ChoiceAnswer):
        top = sorted(a.probabilities.items(), key=lambda kv: -kv[1])[:3]
        dist = ", ".join(f"{k}={v:.2f}" for k, v in top)
        return f"{a.choice} (conf {a.confidence:.2f}; {dist})"
    if isinstance(a, ScoreAnswer):
        return f"score={a.score:.2f} (conf {a.confidence:.2f})"
    raise TypeError(type(a))


@app.command()
def init() -> None:
    """Create ~/.feedlens and the database, applying pending migrations."""
    settings = get_settings()
    ensure_home(settings)
    conn = connect(settings.db_path)
    applied = migrate(conn)
    typer.echo(f"db: {settings.db_path}")
    if applied:
        typer.echo(f"applied migrations: {', '.join(str(v) for v in applied)}")
    else:
        typer.echo("schema up to date")


@app.command()
def decide(
    item: Annotated[str | None, typer.Option("--item", help="Item id from the database")] = None,
    title: Annotated[str | None, typer.Option(help="Ad-hoc item title")] = None,
    text: Annotated[str, typer.Option(help="Ad-hoc item text")] = "",
    kind: Annotated[str, typer.Option(help="video|article|podcast|news")] = "article",
    backend: Annotated[
        str | None, typer.Option(help="fake|ollama|typesafe (default: FEEDLENS_DECISION_BACKEND)")
    ] = None,
) -> None:
    """Evaluate the question set against one item and print the typed answers."""
    if item is None and title is None:
        raise typer.BadParameter("pass --item <id> or --title <text>")
    settings = get_settings()
    if backend is not None:
        settings = settings.model_copy(update={"decision_backend": backend})
    be = get_backend(settings)
    conn = _open(settings)
    profile = _load_profile(conn)
    qs = get_question_set(settings.question_set_version, profile)

    if item is not None:
        target = _load_item(conn, item)
        if target is None:
            typer.echo(f"item not found: {item}")
            raise typer.Exit(code=1)
        cache = DecisionCache(conn, qs, be, max_state_tokens=settings.max_state_tokens)
        answers = asyncio.run(cache.get_or_evaluate(target, profile))
        cache_note = "cache hit" if cache.hits else "evaluated"
    else:
        assert title is not None
        target = Item(
            id="adhoc",
            url_hash="adhoc",
            kind=_kind(kind),
            url="adhoc://",
            title=title,
            text=text,
            created_at="now",
        )
        state = render_state(profile, target, max_tokens=settings.max_state_tokens)
        answers = asyncio.run(be.evaluate(state, qs.questions))
        cache_note = "ad-hoc (not cached)"

    typer.echo(f"item: {target.title}")
    typer.echo(f"backend: {be.id} · question set: {qs.version} · {cache_note}")
    width = max(len(n) for n in answers)
    for name, a in answers.items():
        flag = "calibrated" if a.meta.calibrated else "raw"
        typer.echo(f"  {name.ljust(width)}  {a.type:<6}  {_format_answer(a)}  [{flag}]")


def _kind(value: str) -> ItemKind:
    if value not in ("video", "article", "podcast", "news"):
        raise typer.BadParameter("kind must be video|article|podcast|news")
    return value  # type: ignore[return-value]


@app.command()
def stats() -> None:
    """Counts of items, signals (by month), decisions and sources."""
    conn = _open(get_settings())

    def count(sql: str) -> int:
        return int(conn.execute(sql).fetchone()[0])

    typer.echo(f"sources: {count('SELECT count(*) FROM sources')}")
    typer.echo(f"items: {count('SELECT count(*) FROM items')}")
    typer.echo(f"signals: {count('SELECT count(*) FROM signals')}")
    for row in conn.execute(
        "SELECT substr(occurred_at, 1, 7) AS month, count(*) AS n FROM signals "
        "GROUP BY month ORDER BY month"
    ):
        typer.echo(f"  {row['month']}: {row['n']}")
    typer.echo(f"decisions: {count('SELECT count(*) FROM decisions')}")


@app.command()
def serve() -> None:
    """Run the API + UI."""
    raise typer.Exit(code=_todo("T-2.12"))


@app.command()
def refresh() -> None:
    """Pull → embed → decide → rank."""
    raise typer.Exit(code=_todo("T-2.10"))


def _todo(task: str) -> int:
    typer.echo(f"Not implemented yet — see tasks/mvp-tasks.md ({task})")
    return 2


if __name__ == "__main__":
    app()
