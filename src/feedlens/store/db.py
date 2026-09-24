"""SQLite connection and migration runner (task T-0.3, docs/DATA_MODEL.md).

* WAL journal, foreign keys on, sqlite-vec loaded, `sqlite3.Row` rows.
* Migrations are numbered `NNNN_*.sql` files in `store/migrations/`, applied in order and
  recorded in `schema_migrations`. Never edit an applied migration (AGENTS.md rule 7).
"""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import sqlite_vec

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_MIGRATION_RE = re.compile(r"^(\d{4})_.+\.sql$")


def connect(path: Path | str) -> sqlite3.Connection:
    """Open (creating if needed) the feedlens database with the required extensions."""
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migration_files() -> list[tuple[int, Path]]:
    files: list[tuple[int, Path]] = []
    for p in sorted(MIGRATIONS_DIR.glob("*.sql")):
        m = _MIGRATION_RE.match(p.name)
        if m:
            files.append((int(m.group(1)), p))
    return files


def applied_versions(conn: sqlite3.Connection) -> set[int]:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    return {int(r[0]) for r in conn.execute("SELECT version FROM schema_migrations")}


def migrate(conn: sqlite3.Connection) -> list[int]:
    """Apply pending migrations; return the versions applied in this call."""
    done = applied_versions(conn)
    applied: list[int] = []
    for version, path in migration_files():
        if version in done:
            continue
        # No outer transaction: migration files may contain PRAGMAs (e.g. journal_mode)
        # that cannot run inside one, and `executescript` commits any open transaction
        # anyway. Schema files use IF NOT EXISTS so a partially applied script is re-runnable.
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            (version, datetime.now(UTC).isoformat(timespec="seconds")),
        )
        applied.append(version)
    return applied
