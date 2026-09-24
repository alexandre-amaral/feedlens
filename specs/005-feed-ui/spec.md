# Spec 005 — Feed UI (SPA)

**Status:** approved · **Phase:** 2 · **Depends on:** 003, 004, API

## Why

The daily-use success criterion is decided here. The UI must be faster and calmer than the YouTube home page, and make the "why" visible without clutter (PILOT study: priority-score breakdowns + inline controls + purpose-specific feeds).

## Stack

Vite + Preact + TypeScript, no UI framework; CSS variables, light/dark via `prefers-color-scheme`. Built assets copied to `src/feedlens/api/static/` and served at `/`. Dev: `pnpm dev` with proxy to `:8765`.

## Views

- **Feed** (`/`): tabs `All · Videos · Articles · Podcasts · News`; card = thumbnail (video/news), title, source, published, duration, topic chip with confidence, score pill; actions 👍 👎 less▾ why?. Keyboard: j/k navigate, o open, l like, d dislike, w why, r refresh. Infinite scroll over snapshot (60 items) + "load more" (next 60 from pool).
- **Why drawer**: breakdown table (signal, raw, calibrated, weight, contribution), the profile fragment and rules that fired, and the topic distribution top-3.
- **Profile** (`/profile`): textarea with template, topic taxonomy editor, avoid-list, depth slider, "Apply" with progress.
- **Rules** (`/rules`): list + add form; learned rules marked.
- **Weights** (`/weights`): sliders + λ + ε; live re-rank; presets.
- **Sources** (`/sources`): list with status/last pull/errors; add RSS URL, YouTube channel, OPML upload, Takeout upload, MCP server (JSON); per-source mute/enable.
- **Stats** (`/stats`): items by kind, decisions cache hit rate, calibration reliability chart per field, feedback counts, refresh timings.
- **Refresh indicator**: header button + SSE progress bar; toast on done.

## Requirements

- FR-1 First paint < 1 s on localhost; feed renders from snapshot with no model calls.
- FR-2 SSE client reconnects with backoff; handles `refresh.*`, `feed.updated`, `profile.progress`.
- FR-3 All actions optimistic with rollback on error.
- FR-4 i18n scaffolding (en default, pt-BR strings file) — strings in `web/src/i18n/`.
- FR-5 Accessibility: keyboard reachable, focus visible, contrast AA.

## Acceptance criteria

- AC-1 Lighthouse performance ≥ 95 on the Feed view (localhost build).
- AC-2 Vitest covers breakdown rendering and keyboard navigation reducer.
- AC-3 Two-week daily use by the maintainer without opening YouTube home (self-reported log in `docs/research/eval-log.md`).

## Open questions

- Embedded YouTube player vs. open-in-new-tab: MVP opens in new tab (no watched-fraction signal); reconsider after trial.
