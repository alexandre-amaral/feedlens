# MVP implementation plan

Goal: the maintainer replaces the YouTube home page and his RSS reader with feedlens for two consecutive weeks. Estimates assume a senior engineer working with a coding agent; technical work is fast, third-party/bureaucratic steps (Takeout export, API keys) are not.

## Phase 0 — Foundation (day 1)
Repo tooling, package skeleton, SQLite store + migrations, Decision Contract with `fake` backend, CLI scaffold, CI (ruff, mypy, pytest).
**Exit:** `uv run pytest` green; `feedlens init` creates the db; `feedlens decide --fake` prints answers.

## Phase 1 — Ingestion (days 2–3)
RSS/Atom/podcast, YouTube channel RSS, OPML import, Takeout import, canonicalization, dedup, language detection, `sources`/`import` CLI.
**Exit:** maintainer's real Takeout + OPML imported; `feedlens sources pull` fills `items`.
**External prerequisite (start on day 1):** request Google Takeout (YouTube history, JSON format) — can take hours.

## Phase 2 — Brain + Feed (days 4–7)
Embeddings via Ollama, user vector, hybrid retrieval, `ollama` backend with question set v1, decision cache, scoring, calibrated re-rank, exploration slot, snapshots, feedback + labels + calibration, API, scheduler + SSE, SPA (Feed, Why, Profile, Rules, Weights, Sources, Stats).
**Exit:** `feedlens serve` shows a ranked feed with breakdowns; weight sliders re-rank live; refresh runs in background.

## Phase 3 — Extensions (days 8–10)
MCP client connector + presets (Readwise, Karakeep, Podcast Index, GDELT), news bias (GDELT + MBFC, story clustering), YouTube OAuth (subscriptions + likes), offline eval command, `typesafe` backend stub behind the contract.
**Exit:** news tab with bias bars; `feedlens eval` reports metrics vs baselines.

## Phase 4 — Two-week trial (days 11–25)
Daily use; log friction in `docs/research/eval-log.md`; fix; refit calibration; tune default weights. Ship v0.1.0 tag + README screenshots + `docs/CONTRIBUTING.md` finalized.

## Milestones
| # | Milestone | Verifiable by |
|---|---|---|
| M0 | Skeleton green | CI passes |
| M1 | My history is in | `feedlens stats` shows watched count by month |
| M2 | First ranked feed | screenshot in README |
| M3 | Live controls | video of slider re-rank |
| M4 | News blindspot | story card with bias bar |
| M5 | v0.1.0 | 14-day log complete, tag pushed |

## Risks and mitigations
- Ollama MLX runner lacks logprobs → verbalized fallback with `calibrated=False`, still ranks; native `mlx-lm` backend as follow-up.
- Decision latency > budget → reduce pool K, batch by 8 where isolation is guaranteed, use `qwen3.5:2b` for `clickbait`/`avoid`.
- Takeout delay → develop against fixture history until it arrives.
- GDELT rate limits → cache 15 min, ≤ 1 query / 5 s.
