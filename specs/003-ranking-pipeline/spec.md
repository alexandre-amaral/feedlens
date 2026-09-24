# Spec 003 — Retrieval, scoring, calibration and ranking

**Status:** approved · **Phase:** 2 · **Depends on:** 001, 002, embeddings

## Why

Two-stage ranking with a bounded pool keeps local inference affordable; pointwise typed decisions avoid position bias; calibrated re-ranking keeps the feed's mix honest to the user's history; an exploration slot prevents filter bubbles. (ADR-0005, ADR-0007)

## Pipeline

1. **Embeddings.** `qwen3-embedding:0.6b` over `title + text[:1500]`; user vector = exponentially-decayed mean (half-life 30 days) of embeddings of items with positive signals (watched ≥ 50 %, liked, opened+dwell, like).
2. **Hard filters.** Rules `never`, `mute_source`, `language`, `min/max_duration`; already-seen items excluded unless view = "history".
3. **Retrieval (pool K=200).** RRF over: ANN top-150 by cosine to user vector; BM25 top-100 with profile keywords; recency slice (last 48 h from enabled sources, up to 100). `always` rules force inclusion.
4. **Decisions.** Question set `v1` per item via Decision Contract (cached).
5. **Score.** `score = Σ w_i · s_i` with signals:
   `fit` (Score/4, calibrated), `depth_match` (1 − |depth − profile.depth_pref|/3), `novelty` (Noul), `clickbait` (−Noul), `avoid` (−Noul, hard-drop if calibrated p > 0.9), `recency` (exp decay, half-life 3 days for video/news, 14 for articles/podcasts), `embedding_sim` (cosine), `source_affinity` (learned, [−1, 1]), `bias_diversity` (news only: bonus when outlet bias differs from last N shown).
   Default weights in `settings.weights`; UI-editable.
6. **Calibrated re-rank (Steck).** Greedy selection of top-M (M=60) maximizing `(1−λ)·score − λ·KL(P_feed_topics ‖ P_user_topics)`; `P_user_topics` from decisions on positively-signaled items, smoothed. λ default 0.3.
7. **Exploration.** Every `1/ε`-th slot (ε default 0.1) reserved for the highest-`novelty` item outside top-M, marked in breakdown.
8. **Snapshot.** Persist `feed_snapshots(view, ranked)`; serve from snapshot.

## Calibration

- Labels derived from feedback: `like`/`watched≥50%`/`opened+dwell≥60s` → fit=1; `dislike`/`dismissed`/`less_of_this` → fit=0; `dislike` with reason "clickbait" → clickbait=1; etc.
- Per field, once `n_labels ≥ 30`: fit temperature scaling on raw logits (or on logit(p)); if ECE after fit > 0.1 and `n_labels ≥ 100`, switch to isotonic. Refit nightly and on demand.
- `/api/stats/calibration` returns reliability bins, ECE, n per field.

## Functional requirements

- FR-1 `rank(view) -> list[RankedItem]` runs in < 200 ms for a 2,000-item scored set (no model calls).
- FR-2 Each `RankedItem` has `breakdown` per `docs/DATA_MODEL.md`.
- FR-3 Changing weights/λ/ε/rules/profile invalidates snapshots and re-ranks; changing profile also changes `state_hash` → decisions re-evaluated lazily on next refresh (not synchronously).
- FR-4 Views: `default`, `videos`, `articles`, `podcasts`, `news`, `history`.
- FR-5 Offline evaluation command `feedlens eval --holdout 0.2` replays historical signals: precision@10, recall@50, ECE, vs. baselines `recency` and `embedding_only`. Results appended to `docs/research/eval-log.md`.

## Acceptance criteria

- AC-1 Unit tests for RRF, greedy calibrated re-rank, exploration slot, weight changes (with fake decisions).
- AC-2 `feedlens eval` runs on the maintainer's Takeout history and reports metrics for all three strategies.
- AC-3 Performance FR-1 measured in a test with synthetic data.

## Open questions

- Should `fit` be replaced by a learned linear model over all decision fields once labels ≥ 300? Candidate for v0.2 (readprism-style learned weights).
