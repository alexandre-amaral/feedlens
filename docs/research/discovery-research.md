# Discovery research (2026-09-24)

Condensed findings that shaped the specs and ADRs. [C] confirmed from a primary/secondary source; [I] inference.

## TypeSafe Jev / System One

- Announced ~2026-09-15. "System One models" make fast, structured decisions and do not generate text. Single model `jev-1.13.0`; closed weights, hosted API, early-access waitlist. [C] https://docs.typesafe.ai/models.md
- Trained with RLCD (Reinforcement Learning for Calibrated Decisions); no paper, no public ECE/Brier. [C]
- API `POST /v1/systemone` with `state`, `model`, `questions`; primitives Noul (p), Choice (≤255 labels, probabilities + confidence), Score (2–10 levels, weighted mean). Questions evaluated in parallel and in isolation. Pricing $0.042/M input tokens, output free; 70–500 ms; 64k context (32k state); text only. [C] https://docs.typesafe.ai/api.md
- Documented weaknesses: literal negations, no counting, accuracy drops with irrelevant state, not adversarially robust. [C]
- OSS adapter `typesafe-ai/system-one-adapter-python` (MIT) emulates the API over OpenAI/Anthropic/Gemini/any OpenAI-compatible endpoint; probabilities are **verbalized by the LLM**, not derived from logprobs. [C]
- Criticism: self-graded benchmarks; "0% hallucination" = "0% out-of-schema"; calibration untested externally; CEO agreed with "zero-shot classifier". [C]
- Open reimplementations: `rorshopping/jev-on-a-laptop` (MLX single-pass field scoring; raw softmax badly calibrated), `bnsd55/jevmlx`, `Heman10x-NGU/Verdict-open-jev` (ModernBERT-151M + temperature scaling). [C]
- Only feed application found: `iikareem/skillfeed` (one Score per article, profile in state). [C]

## Source feasibility

| Source | Live API | Bulk history | Candidates | Notes |
|---|---|---|---|---|
| YouTube | subs, likes, playlists (OAuth; 10k units/day; `search`=100 units) | Google Takeout `watch-history.json` | channel RSS (no quota) | Watch history removed from API in 2016 [C] |
| Spotify | recently-played (50), top, saved, following; Dev Mode ≤5 users; recommendations/audio-features removed Nov 2024 | Extended streaming history export | search (limit 10) | Extended quota needs 250k MAU [C] |
| Ground News | none | — | — | No public API; scrapers only [C] |
| News bias | MBFC Data API (limited tier), AllSides (paid), GDELT DOC 2.0 (free) | — | GDELT | [C] |
| Podcasts | Pocket Casts unofficial API; Apple none | OPML | Podcast Index API, RSS | [C] |
| Articles | Readwise Reader hosted MCP; Karakeep official MCP; Reddit OAuth (~100 QPM) | Reddit GDPR export | RSS, HN Algolia | Pocket shut down Jul 2025 [C] |
| Books | Hardcover GraphQL | Goodreads/StoryGraph CSV | Open Library | [C] |
| Film/TV | Trakt (new apps likely need VIP since Aug 2026) | Letterboxd CSV (API refuses personal/LLM/recommendation projects) | TMDB | [C] |

## Local models

- SLMs: Qwen3.5 0.8B/2B/4B/9B (Apache 2.0, Mar 2026); Gemma 4 E2B/E4B; Phi-4-mini (MIT); SmolLM3-3B. [C]
- Runtimes: Ollama (JSON `format`; logprobs on OpenAI-compatible endpoint; v0.33.1 structured output on MLX runner); llama.cpp GBNF; Outlines + mlx-lm. [C]
- Verbalized and raw-logprob confidences are unreliable without post-hoc calibration (arXiv 2608.04899, 2609.10996). [C]
- Embeddings (MMTEB): Qwen3-Embedding-0.6B 64.3 / 4B 69.5 (Apache); multilingual-e5-large-instruct 63.2 (MIT); bge-m3 (MIT, hybrid). Rerankers: Qwen3-Reranker-0.6B, bge-reranker-v2-m3. [C]

## Projects to learn from

Miniflux (Go, Apache 2.0), Karakeep (AGPL, Ollama tagging, MCP), rssfilter (embeddings + random discovery), readprism (8 weighted signals, learned per-user weights), PersonalRSS (Always/Never rules + logistic + thresholds), Gorse (Go engine with LLM rankers), Bluesky feed-generator, Sill, Fediway (sources → filters → scorers → samplers), Tournesol/Solidago (pairwise preference), X algorithm (pointwise scoring from user context; "promptable feeds" May 2026), RankLLM.

## Design literature

- Two-stage with K≈200 pool, hybrid retrieval, ensemble with popularity/similarity (arXiv 2604.16318).
- Listwise LLM ranking has position bias; prefer pointwise (InvariRank, SIGIR 2026).
- Editable natural-language profiles shift recommendations without retraining (UPR, arXiv 2402.05810); steering reliable at coarse grain only (SteerEval, arXiv 2601.21105).
- Usable feed controls: score breakdowns, inline feedback, purpose-specific feeds (PILOT, arXiv 2509.19615).
- Calibrated recommendations (Steck 2018; survey arXiv 2507.02643): greedy re-rank trading relevance vs KL to the user's category distribution.
- LLMs competitive near cold start (Sanner et al., RecSys'23).
