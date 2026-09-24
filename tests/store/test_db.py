import sqlite3
import struct
from pathlib import Path

from feedlens.store.db import connect, migrate


def _tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("select name from sqlite_master where type in ('table','view')").fetchall()
    return {r[0] for r in rows}


def test_connect_sets_pragmas_and_loads_vec(tmp_path: Path) -> None:
    conn = connect(tmp_path / "t.db")
    assert conn.execute("pragma journal_mode").fetchone()[0] == "wal"
    assert conn.execute("pragma foreign_keys").fetchone()[0] == 1
    assert conn.execute("select vec_version()").fetchone()[0].startswith("v")
    assert conn.row_factory is sqlite3.Row


def test_migrate_applies_schema_v1(tmp_path: Path) -> None:
    conn = connect(tmp_path / "t.db")
    applied = migrate(conn)
    assert applied == [1]
    names = _tables(conn)
    for t in (
        "sources",
        "items",
        "items_fts",
        "items_vec",
        "signals",
        "decisions",
        "feedback",
        "labels",
        "calibration",
        "profile",
        "rules",
        "settings",
        "feed_snapshots",
        "user_vector",
        "schema_migrations",
    ):
        assert t in names, t
    assert conn.execute("select version from schema_migrations").fetchall()[0][0] == 1


def test_migrate_is_idempotent(tmp_path: Path) -> None:
    conn = connect(tmp_path / "t.db")
    assert migrate(conn) == [1]
    assert migrate(conn) == []
    # a fresh connection to the same file also sees it as applied
    assert migrate(connect(tmp_path / "t.db")) == []


def test_vec_table_round_trip(tmp_path: Path) -> None:
    conn = connect(tmp_path / "t.db")
    migrate(conn)
    vec = struct.pack("1024f", *([0.0] * 1023 + [1.0]))
    conn.execute("insert into items_vec(item_id, embedding) values (?, ?)", ("i1", vec))
    row = conn.execute(
        "select item_id, distance from items_vec where embedding match ? and k = 1", (vec,)
    ).fetchone()
    assert row["item_id"] == "i1"
    assert row["distance"] == 0.0


def test_fts_trigger_indexes_items(tmp_path: Path) -> None:
    conn = connect(tmp_path / "t.db")
    migrate(conn)
    conn.execute(
        "insert into items(id,url_hash,kind,url,title,text,created_at) values (?,?,?,?,?,?,?)",
        ("i1", "h1", "article", "https://x/a", "Rust async deep dive", "tokio internals", "2026"),
    )
    hit = conn.execute("select rowid from items_fts where items_fts match 'tokio'").fetchall()
    assert len(hit) == 1
