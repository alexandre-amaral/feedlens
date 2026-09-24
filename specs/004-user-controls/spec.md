# Spec 004 — User controls: profile, rules, weights, feedback

**Status:** approved · **Phase:** 2 · **Depends on:** 003

## Why

Constitution Article I. Four complementary control surfaces, each with a distinct effect and latency: rules (hard, instant), weights (soft, instant), natural-language profile (changes decisions, lazy), feedback (changes calibration and affinity, accumulative). Literature: editable NL profiles shift recommendations without retraining (UPR); coarse steering works, niche steering is unreliable (SteerEval) — so rules exist for the niche cases.

## Profile

- Free text ≤ 600 tokens. Suggested template rendered in the UI: *"I want more … / less … / I'm currently focused on … / avoid …"*.
- Topic taxonomy: list of ≤ 40 `{label, description}`; seeded from a default set and from the top-20 clusters of the user's watched history (k-means on embeddings, labels proposed via a `Choice`-free summarization prompt — the only text-generation call in the system, optional).
- Avoid-list: strings fed to the `avoid` Noul.
- `depth_pref` 0–3 slider.
- Saving the profile: rank immediately with cached decisions; schedule re-evaluation of the pool in background; UI shows "profile applied to 120/200 items" progress via SSE.

## Rules

Kinds: `always` (pin: match → forced into pool and top), `never` (drop), `mute_source`, `language` (allow-list), `min_duration`, `max_duration`. Match on `title`/`text` regex (case-insensitive), `topic` label, `source_id`, `kind`. Evaluated as hard filters in retrieval. UI lists rules with hit counts from the last snapshot.

## Weights

Sliders for each signal in 003 (range −1..1, default set) plus λ and ε. Changes debounce 300 ms → `PUT /api/weights` → re-rank → SSE `feed.updated`. "Reset to defaults" and "Save as preset" (presets stored in settings).

## Feedback

Per card: 👍, 👎 (with optional reason: clickbait / not my topic / seen it / too shallow / too long), "less of this ▾" (topic / source / kind), "why?" (opens breakdown). Implicit: `opened` (link click), `watched` (only when the player is embedded — MVP records opened only), `dismissed` (swipe/hide).
Effects: labels for calibration (003), source affinity ±0.1 with decay, user vector update, `less_of_this` creates a soft rule (weight −0.5 on that target, visible in Rules as "learned").

## API

`GET/PUT /api/profile` · `GET/POST/DELETE /api/rules` · `GET/PUT /api/weights` · `POST /api/feedback` · `GET /api/items/{id}/why`.

## Acceptance criteria

- AC-1 Adding a `never` regex removes matching items on the next `GET /api/feed` without a model call.
- AC-2 Moving the `fit` weight slider reorders the feed within 500 ms end-to-end.
- AC-3 Editing the profile marks decisions stale and re-evaluates in background; the feed keeps serving meanwhile.
- AC-4 Thirty 👍/👎 on the same field triggers a calibration fit; `/api/stats/calibration` shows ECE.

## Open questions

- Should "less of this → source" become `mute_source` after N repeats? MVP: no auto-escalation; show a suggestion.
