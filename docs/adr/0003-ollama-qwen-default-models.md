# ADR-0003 — Ollama with Qwen3.5-4B (decisions) and Qwen3-Embedding-0.6B (embeddings) as defaults

Date: 2026-09-24 · Status: accepted

## Context
Need multilingual (PT-BR + EN) small models with structured output on Apple Silicon. Qwen3.5 small models (Apache 2.0, Mar 2026) lead their class; Qwen3-Embedding-0.6B scores 64.3 on MMTEB with 1024-d vectors. Ollama ≥ 0.33 has an MLX runner with structured outputs and exposes logprobs on its OpenAI-compatible endpoint.

## Decision
Ollama is the default runtime; models configurable via env. Decisions run in non-thinking mode. An `mlx-lm` backend (jev-on-a-laptop style single-pass field scoring) is a documented future option.

## Consequences
+ One-command install for users; portable to Linux/NVIDIA via the same Ollama API.
− Slower than a native MLX single-pass scorer; acceptable within the 5-minute refresh budget for a 200-item pool.
