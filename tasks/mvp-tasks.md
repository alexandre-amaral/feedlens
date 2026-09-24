# MVP tasks

Format: `- [ ] T-<phase>.<n> <title> — spec:<id> · depends_on:<ids> · est:<S|M|L>`. S ≈ under 1 h with an agent, M ≈ half day, L ≈ a day. Mark `[x]` in the commit that completes the task. Keep order; parallelize only within the same phase when `depends_on` allows.

## Phase 0 — Foundation
- [x] T-0.1 Tooling: `pyproject.toml` (uv, ruff, mypy strict, pytest), `.pre-commit-config.yaml`, GitHub Actions CI (lint+type+test on macOS + ubuntu) — spec:— · depends_on:— · est:S
- [x] T-0.2 Config: `feedlens.config.Settings` (pydantic-settings, `FEEDLENS_*` env, `~/.feedlens` paths) — depends_on:T-0.1 · est:S
- [ ] T-0.3 Store: SQLite connection (WAL, foreign keys, sqlite-vec load), migration runner, `0001_init.sql` from `docs/DATA_MODEL.md` — depends_on:T-0.2 · est:M
- [ ] T-0.4 Decision Contract: `Noul/Choice/Score`, `Answers`, `DecisionBackend` protocol, `FakeBackend`, math tests (spec 001 FR-1/2) — spec:001 · depends_on:T-0.1 · est:M
- [ ] T-0.5 Question set `v1` (`feedlens/decisions/questions.py`) + state renderer (profile + item → compact text, token budget) — spec:001 · depends_on:T-0.4 · est:S
- [ ] T-0.6 Decision cache (`decisions` table, `state_hash`) — spec:001 · depends_on:T-0.3,T-0.5 · est:S
- [ ] T-0.7 CLI scaffold (`typer`): `init`, `decide --fake`, `stats` — depends_on:T-0.3,T-0.6 · est:S

## Phase 1 — Ingestion
- [ ] T-1.1 Canonical `Item`/`Signal` models, URL canonicalization, `url_hash`, upsert with merge rules — spec:002 · depends_on:T-0.3 · est:S
- [ ] T-1.2 `rss` connector (feedparser, conditional GET, podcast enclosures → kind=podcast) + fixtures — spec:002 · depends_on:T-1.1 · est:M
- [ ] T-1.3 `youtube_rss` connector (channel_id/handle resolution, `videos.xml` parsing, video_id/thumbnail metadata) — spec:002 · depends_on:T-1.2 · est:S
- [ ] T-1.4 `opml` import → sources (idempotent; YouTube OPML recognition) — spec:002 · depends_on:T-1.2,T-1.3 · est:S
- [ ] T-1.5 `takeout` importer (JSON + HTML, ads filtered, ≥50k rows < 60 s, signals + stub items) — spec:002 · depends_on:T-1.1 · est:M
- [ ] T-1.6 Language detection + per-host rate limiter + per-source error isolation — spec:002 · depends_on:T-1.2 · est:S
- [ ] T-1.7 CLI: `sources add rss|youtube|opml`, `sources list|pull`, `import takeout` — spec:002 · depends_on:T-1.2..T-1.6 · est:S

## Phase 2 — Brain, API, UI
- [ ] T-2.1 Embedder via Ollama `/api/embed`, batch 32, `items_vec` upsert; user vector with 30-day half-life — spec:003 · depends_on:T-1.7 · est:M
- [ ] T-2.2 Hybrid retrieval: FTS5 BM25 + sqlite-vec ANN + recency slice, RRF, K=200, hard-filter rules — spec:003 · depends_on:T-2.1 · est:M
- [ ] T-2.3 `ollama` backend: JSON `format` schema per question, logprob-based distribution when available, verbalized fallback flagged, semaphore(4), retries — spec:001 · depends_on:T-0.5 · est:L
- [ ] T-2.4 Scoring: signals + weights + breakdown; settings defaults — spec:003 · depends_on:T-2.2,T-0.6 · est:M
- [ ] T-2.5 Calibrated re-rank (greedy KL) + exploration slot + snapshots + views — spec:003 · depends_on:T-2.4 · est:M
- [ ] T-2.6 Feedback events → labels → source affinity → user vector update; `less_of_this` learned rule — spec:004 · depends_on:T-2.5 · est:M
- [ ] T-2.7 Calibration: temperature scaling + isotonic fallback per field, ECE, nightly refit, `/api/stats/calibration` — spec:003 · depends_on:T-2.6 · est:M
- [ ] T-2.8 Profile/rules/weights models + API (`GET/PUT`), invalidation semantics (rank vs re-decide) — spec:004 · depends_on:T-2.5 · est:M
- [ ] T-2.9 Optional article full-text via `trafilatura` behind a flag; evaluate quality on 50 feeds — spec:002 · depends_on:T-1.2 · est:S
- [ ] T-2.10 RefreshJob (pull→embed→decide→rank→snapshot), lock + coalescing, event bus — spec:006 · depends_on:T-2.5,T-2.3 · est:M
- [ ] T-2.11 APScheduler in lifespan, battery guard, `FEEDLENS_SCHEDULER` — spec:006 · depends_on:T-2.10 · est:S
- [ ] T-2.12 FastAPI app: feed, feedback, items/why, sources, refresh (202), SSE `/api/events`, static mount — spec:005/006 · depends_on:T-2.8,T-2.10 · est:M
- [ ] T-2.13 SPA scaffold (Vite+Preact+TS, router, API client, SSE client, i18n en/pt-BR, theme) — spec:005 · depends_on:T-2.12 · est:M
- [ ] T-2.14 Feed view + cards + keyboard + Why drawer — spec:005 · depends_on:T-2.13 · est:L
- [ ] T-2.15 Profile, Rules, Weights views (live re-rank, presets) — spec:005 · depends_on:T-2.14 · est:M
- [ ] T-2.16 Sources view (add RSS/YouTube/OPML/Takeout upload) + Stats view (calibration chart) — spec:005 · depends_on:T-2.14 · est:M
- [ ] T-2.17 Build pipeline: `pnpm build` → `src/feedlens/api/static/`; `feedlens serve` opens browser — spec:005 · depends_on:T-2.13 · est:S
- [ ] T-2.18 Perf tests: re-rank < 200 ms @ 2,000 items; refresh budget doc — spec:003/006 · depends_on:T-2.5,T-2.10 · est:S

## Phase 3 — Extensions
- [ ] T-3.1 MCP client connector (stdio + HTTP), JSONPath mapping, secrets file, validation errors — spec:007 · depends_on:T-1.7 · est:L
- [ ] T-3.2 MCP presets: readwise, karakeep, podcastindex, gdelt + tool-discovery UI in Sources — spec:007 · depends_on:T-3.1,T-2.16 · est:M
- [ ] T-3.3 News bias: GDELT connector, MBFC table loader (API tier or CSV), domain matching, story clustering, `bias_diversity`/`factuality` signals — spec:008 · depends_on:T-2.5 · est:L
- [ ] T-3.4 News UI: bias/factuality chips, story card with bias bar, per-outlet override — spec:008 · depends_on:T-3.3,T-2.14 · est:M
- [ ] T-3.5 `youtube_oauth` connector: subscriptions.list + liked videos (playlist LL), token storage, quota-aware — spec:002 · depends_on:T-1.3 · est:M
- [ ] T-3.6 `feedlens eval --holdout` with baselines recency/embedding_only; write `docs/research/eval-log.md` — spec:003 · depends_on:T-2.7 · est:M
- [ ] T-3.7 `typesafe` backend (lazy import `typesafe-sdk`, map primitives 1:1, mark `calibrated=backend_claims`) — spec:001 · depends_on:T-0.4 · est:S

## Phase 4 — Trial and release
- [ ] T-4.1 Daily-use log, 14 days; friction list; fixes — depends_on:Phase 2 · est:L
- [ ] T-4.2 Default weights tuned from eval + trial; README screenshots; CONTRIBUTING finalized; `v0.1.0` tag — depends_on:T-4.1 · est:S
