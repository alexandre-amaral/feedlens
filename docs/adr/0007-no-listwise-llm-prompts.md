# ADR-0007 — No listwise LLM ranking prompts

Date: 2026-09-24 · Status: accepted

## Context
See ADR-0005. Listwise prompts ("rank these 20") are order-sensitive and non-cacheable.

## Decision
All model calls are pointwise `(user_state, item)`. Batching multiple items in one request is allowed only when the backend guarantees isolation (Jev-style array state) — otherwise one item per prompt.

## Consequences
+ Cache hit on unchanged items; deterministic re-rank.
− Diversity is handled by the re-rank stage, not by the model.
