# Spec 008 — News with bias & factuality metadata

**Status:** approved · **Phase:** 3 · **Depends on:** 002, 003

## Why

Ground News (the reference product) has no public API and forbids scraping of personal feeds. The same "blindspot" value can be rebuilt from open data: GDELT for coverage across outlets, MBFC (and optionally AllSides) for outlet-level bias/factuality. (ADR-0009)

## Design

- Candidate source: GDELT DOC 2.0 API (`https://api.gdeltproject.org/api/v2/doc/doc?query=…&mode=artlist&format=json`), one query per user "news topic" (from profile topics flagged `news: true`), `timespan=24h`, max 100 records/query, ≥ 5 s between calls (GDELT rate limit).
- Outlet metadata: MBFC dataset via RapidAPI limited tier or a user-provided CSV; cached in `~/.feedlens/cache/mbfc.json`, refreshed monthly. Fields: `bias` (left, left-center, center, right-center, right, …), `factual` (very high … very low), `country`. Match by registered domain.
- Story clustering: group news items from the last 48 h by embedding similarity (cosine ≥ 0.82, agglomerative); a cluster is a "story". Story metadata: outlets, bias distribution, `blindspot_score` = 1 − entropy-normalized balance.
- Signals for ranking: `bias_diversity` (bonus for an outlet bias under-represented in the last 20 shown news items), `factuality` (penalty below "mixed"), `story_coverage` (log #outlets).
- UI: news cards show outlet, bias chip, factuality chip; a story card shows the bias bar (left/center/right shares) and lets the user open coverage from each side.
- Explicit non-goal: feedlens does not rate outlets itself; it displays third-party ratings with attribution and lets the user override per outlet.

## Acceptance criteria

- AC-1 With 5 news topics, a refresh yields ≥ 50 news items with bias metadata for ≥ 70 % of them (English outlets).
- AC-2 Story clustering groups the same event from ≥ 3 outlets in a fixture test.
- AC-3 Bias bar renders and per-outlet override persists.

## Open questions

- PT-BR outlets: MBFC coverage is thin. Allow a community CSV (`docs/data/outlets-ptbr.csv`) as an additional table; start empty.
- AllSides licensing: paid; keep out of MVP, support as an optional CSV import.
