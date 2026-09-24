# AGENTS.md — rules for coding agents working on feedlens

Read `.specify/memory/constitution.md` first. It wins over this file; this file wins over ad-hoc judgment.

## Project shape

- Python 3.12 package in `src/feedlens/` (FastAPI, Pydantic v2, SQLite + sqlite-vec, httpx, feedparser, apscheduler, mcp). Managed with `uv`.
- SPA in `web/` (Vite + Preact + TypeScript), built to `src/feedlens/api/static/` and served by FastAPI.
- Specs in `specs/<id>-<slug>/spec.md`; plan in `plans/`; backlog in `tasks/mvp-tasks.md`; ADRs in `docs/adr/`.

## Commands

```bash
uv sync                      # install
uv run pytest -q             # tests
uv run ruff check . && uv run ruff format .   # lint/format
uv run mypy                  # types (strict)
pre-commit install           # optional: run ruff+mypy on every commit
uv run feedlens --help       # CLI
cd web && pnpm i && pnpm dev # SPA dev server (proxies /api to :8765)
```

## Coding rules

1. **Decision Contract is sacred.** All model calls go through `feedlens.decisions.contract` (`Noul`, `Choice`, `Score`) and a `DecisionBackend`. Never call Ollama or any LLM directly from ranking, ingestion or API code.
2. **Pointwise, batch-independent scoring.** A candidate's decisions depend only on `(user_state, item)`. Never on other candidates in the batch.
3. **Decisions are cached by `(item_id, question_set_version, backend_id)`.** Changing weights, rules or profile must not trigger re-scoring; it must trigger re-ranking.
4. **Every score is explainable.** The ranking output carries a `breakdown` listing each signal, its raw value, weight and contribution. The UI renders it; tests assert it.
5. **Local by default.** No network call except to configured sources, Ollama on localhost, and explicitly enabled backends. No telemetry.
6. **Small models, small prompts.** Keep `state` under 4k tokens; profile text under 600 tokens. Irrelevant state degrades accuracy.
7. **Schema migrations** are numbered SQL files in `src/feedlens/store/migrations/`; never edit an applied migration.
8. **Tests** use a temp SQLite db and a `FakeDecisionBackend` that returns deterministic probabilities. Ollama is never required in CI.
9. **Types everywhere.** `mypy --strict` on `src/`; `tsc --noEmit` on `web/`.
10. **Commits:** Conventional Commits, single author, no attribution trailers.

## When a spec is unclear

Pick the smallest interpretation that satisfies the acceptance criteria, implement it, and append the question to the spec's "Open questions" list in the same commit. Do not ask in chat unless blocked.

## Do not

- Do not add Karakeep, Miniflux or any external service as a hard dependency (ADR-0004).
- Do not introduce listwise LLM ranking prompts (ADR-0007).
- Do not use verbalized probabilities ("give me a confidence 0–1") as calibrated confidence (ADR-0006).
- Do not store raw OAuth tokens outside `~/.feedlens/secrets.json` (0600).
