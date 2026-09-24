# ADR-0005 — Two-stage ranking with bounded pool and pointwise decisions

Date: 2026-09-24 · Status: accepted

## Context
Local inference budget is small. Literature (arXiv 2604.16318) shows smaller pools (K≈200) beat K=1000 with LLM rerankers, hybrid retrieval avoids embedding-only recall collapse, and cross-candidate prompts introduce position bias (InvariRank, SIGIR 2026). X's open-sourced algorithm follows the same rule: score each candidate from user context only.

## Decision
Hybrid retrieval (ANN ∪ BM25 ∪ recency, RRF) to K=200, then pointwise typed decisions per item, then a transparent linear score, then calibrated re-rank + exploration.

## Consequences
+ Cost linear in K, cacheable per item, explainable.
− No listwise "compare these two" reasoning; accepted.
