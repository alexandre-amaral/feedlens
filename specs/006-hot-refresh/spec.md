# Spec 006 — Hot refresh

**Status:** approved · **Phase:** 2 · **Depends on:** 002, 003

## Definition (agreed in discovery — all three)

1. **On-demand refresh**: a button/shortcut/CLI pulls sources, embeds and decides only new items, re-ranks, and updates the UI live.
2. **Background refresh**: an in-process scheduler runs the same job every `refresh_interval_min` (default 15) while `feedlens serve` is running; the UI updates via SSE without reload.
3. **Instant re-rank**: any change to rules, weights, λ, ε or profile re-ranks from cached decisions immediately (< 200 ms server-side, < 500 ms end-to-end), never blocking on model calls.

## Design

- `RefreshJob` = pull → canonicalize → embed(new) → decide(pool ∖ cached) → rank → snapshot → emit events. Stages are idempotent and resumable; a single job runs at a time (lock); a second trigger while running is coalesced into "run again after".
- APScheduler `AsyncIOScheduler` inside the FastAPI lifespan; misfire grace 5 min; paused when `FEEDLENS_SCHEDULER=off`.
- Events bus (in-process asyncio queue) → SSE endpoint `/api/events`; event types: `refresh.started {job_id}`, `refresh.progress {stage, done, total}`, `refresh.done {new_items, decided, duration_s}`, `refresh.failed {source_id, error}`, `feed.updated {view}`, `profile.progress {done, total}`.
- Decisions for items outside the pool are never computed (cost control). Pool-only scoring keeps a 500-new-item refresh under 5 min on M1 Air (≈ 200 decisions × ~1.2 s / 4 concurrent ≈ 60 s + embeddings).
- Laptop-friendly: scheduler skips runs when on battery below 20 % (via `pmset -g batt` on macOS; best-effort), configurable.

## Acceptance criteria

- AC-1 `POST /api/refresh` returns 202 with `job_id`; SSE streams progress; UI shows new items without reload.
- AC-2 Weight change → `feed.updated` within 500 ms measured in an integration test with 2,000 synthetic scored items.
- AC-3 Two simultaneous refresh triggers result in at most two sequential runs.
- AC-4 Scheduler runs unattended for 24 h without memory growth > 50 MB (leak test in CI nightly, optional).

## Open questions

- Should refresh be a separate process (launchd agent) so the feed updates when the server isn't running? MVP: in-process; provide `feedlens refresh` for cron/launchd users.
