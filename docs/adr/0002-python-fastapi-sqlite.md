# ADR-0002 — Python 3.12 + FastAPI + SQLite (FTS5 + sqlite-vec)

Date: 2026-09-24 · Status: accepted

## Context
Local, lightweight, single-user MVP on a MacBook Air. The ML/MCP/Ollama ecosystem is Python-first. Postgres/pgvector would add a service to run.

## Decision
One Python process: FastAPI (API + static SPA), APScheduler, SQLite in WAL mode with FTS5 for BM25 and sqlite-vec for ANN. Package managed with `uv`, linted with `ruff`, typed with `mypy --strict`.

## Consequences
+ Zero external services besides Ollama; single file backup.
− sqlite-vec brute-force is fine up to ~1M vectors; beyond that, revisit (not an MVP concern).
