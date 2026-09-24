# Architecture

## Overview

feedlens is a single Python process (FastAPI + APScheduler) with an embedded SQLite database and a Preact SPA, talking to Ollama on localhost. Five stages form the pipeline; each is a module with a narrow interface so it can be replaced or tested in isolation.

```
 sources ──► ingest ──► store ──► retrieve ──► decide ──► rank ──► feed API ──► SPA
 (RSS, Takeout,         (SQLite +   (hybrid    (Decision   (formula +           (cards +
  OPML, MCP,             sqlite-vec) BM25+ANN)  Contract)   calibration +        breakdown +
  GDELT/MBFC)                                                exploration)         controls)
                                                   ▲                                 │
                                                   └──── feedback ◄──────────────────┘
```

## Modules

### `feedlens.ingest` — connectors
Each connector implements `Connector.pull(since) -> Iterable[RawItem]` and `Connector.signals(since) -> Iterable[RawSignal]`. Connectors in MVP:

| Connector | Candidates | Signals |
|---|---|---|
| `rss` | any RSS/Atom feed (articles, podcast enclosures) | — |
| `youtube_rss` | `youtube.com/feeds/videos.xml?channel_id=` per subscribed channel | — |
| `takeout` | — | `watch-history.json` → watched items with timestamps |
| `opml` | imports feed lists (RSS readers, podcast apps) | — |
| `youtube_oauth` (phase 3) | — | subscriptions, liked videos |
| `mcp` | generic client for MCP servers exposing list/search tools (Readwise, Karakeep, Podcast Index, GDELT) | reads/highlights where the server exposes them |
| `news_bias` | GDELT DOC 2.0 articles | MBFC source bias/factuality table (cached) |

Output is a **canonical Item**: `id, kind (video|article|podcast|news), source_id, url, title, text (description/transcript excerpt), author, published_at, duration_s, language, metadata JSON`. Dedup by canonical URL hash.

### `feedlens.store` — SQLite
Single file `~/.feedlens/feedlens.db`, WAL mode, FTS5 for BM25, sqlite-vec for embeddings. Schema in `docs/DATA_MODEL.md`. Migrations are numbered SQL files applied at startup.

### `feedlens.embed`
`Embedder.embed(texts) -> list[vector]` via Ollama `/api/embed` with `qwen3-embedding:0.6b` (1024-d). Text = title + first 1,500 chars. Also builds the **user vector** = time-decayed mean of embeddings of positively-signaled items.

### `feedlens.retrieve`
Hybrid retrieval over items not yet seen: BM25 (FTS5 over title/text using profile keywords) ∪ ANN (sqlite-vec cosine to user vector) ∪ **recency slice** (everything published in the last 48 h from subscribed sources). Reciprocal rank fusion, pool capped at `K=200`. Deterministic rules (`never`, `mute source`) are applied here as hard filters.

### `feedlens.decisions` — the Decision Contract
```python
Noul(instructions, criteria: {true: str, false: str} | None)      -> {p: float}
Choice(instructions, criteria: dict[label, description])           -> {choice, probabilities, confidence}
Score(instructions, criteria: list[level_description], 2..10)      -> {score, probabilities, confidence}
DecisionBackend.evaluate(state: str | dict, questions: dict[str, Question]) -> Answers
```
Backends: `ollama` (default; constrained JSON via Ollama `format` + label logprobs from `/v1/chat/completions` when available, fallback to verbalized distribution flagged `calibrated=False`), `typesafe` (Jev API, opt-in), `fake` (tests). The **MVP question set v1** (per item, state = compact profile + item):

| name | type | purpose |
|---|---|---|
| `topics` | Choice (user's topic taxonomy, ≤ 40 labels) | category for calibration + rules |
| `fit` | Score 0–4 ("irrelevant" … "exactly what the profile asks") | main relevance |
| `depth` | Score 0–3 (shallow … deep/long-form) | matches profile preference |
| `clickbait` | Noul | penalty |
| `novelty` | Noul ("says something the user hasn't seen this week") | diversity |
| `avoid` | Noul ("matches any avoid-list entry") | hard/soft penalty |

Answers are cached in `decisions(item_id, question_set_version, backend_id)`.

### `feedlens.calibrate`
Per field, fits temperature scaling (fallback: isotonic) on `(raw_prob, feedback_label)` pairs once ≥ 30 labels exist. Stores parameters; `calibrated_p = calibrate(field, raw_p)`. Reports ECE in the UI.

### `feedlens.rank`
```
score = Σ_i  w_i · signal_i(item)            # signals: fit, depth_match, novelty, −clickbait, −avoid,
                                             # recency, source_affinity, embedding_sim, bias_diversity
then: calibrated re-rank (Steck): greedy pick maximizing (1−λ)·score − λ·KL(feed_topics ‖ user_topics)
then: exploration slot: every N-th position reserved for a random high-novelty item (ε configurable)
```
Weights `w_i`, `λ`, `ε` and thresholds live in `settings` and are user-editable. The output carries `breakdown` per item. Re-ranking reads cached decisions only, so it is O(pool) and sub-200 ms.

### `feedlens.feedback`
Events: `like`, `dislike`, `less_of_this(topic|source|kind)`, `why_opened`, `opened`, `watched(duration)`, `dismissed`. Explicit events create labels for calibration; implicit events update source affinity and the user vector with decay.

### `feedlens.api` — FastAPI
`GET /api/feed?view=` · `POST /api/feedback` · `GET/PUT /api/profile` · `GET/PUT /api/rules` · `GET/PUT /api/weights` · `POST /api/refresh` · `GET /api/events` (SSE) · `GET /api/items/{id}/why` · `GET /api/sources`, `POST /api/sources` · `GET /api/stats/calibration`.

### `feedlens.scheduler` — hot refresh
APScheduler in-process: `pull` every 15 min (configurable), `embed+decide` for new items immediately after pull, `rank` on demand. UI receives `refresh.started/progress/done` over SSE. `POST /api/refresh` triggers the same job out of band. Editing profile/rules/weights calls `rank` only.

### `web/` — SPA
Preact + Vite. Views: **Feed** (cards, filter by kind, "why?" drawer with breakdown), **Profile** (NL text + topic taxonomy), **Rules** (always/never/mute/source), **Weights** (sliders with live re-rank), **Sources** (add RSS/OPML/Takeout/MCP), **Stats** (calibration curves, ECE, feedback counts).

## Data flow for one refresh

1. Scheduler/`POST /refresh` → connectors pull since last cursor → canonical items upserted (dedup).
2. New items embedded in batches of 32.
3. Retrieval builds pool K=200 from unseen items.
4. Items in pool lacking decisions for `question_set_version` are evaluated (batch of 8 items per Ollama call where the backend supports arrays; otherwise 1 item/call, 4 concurrent).
5. Rank computes scores, calibrated re-rank, exploration slot; writes `feed_snapshot`.
6. SSE `refresh.done` → SPA reloads feed.

## Non-goals (MVP)
Multi-user, cloud deployment, Spotify/books/movies connectors, transcript fetching, listwise LLM ranking, MLX-native backend, mobile.
