# ADR-0001 — The Decision Contract (Noul/Choice/Score) is the central interface

Date: 2026-09-24 · Status: accepted

## Context
The project was conceived as "JEV-based". Research showed TypeSafe's Jev is a closed, hosted, early-access model with no public calibration evidence, while its API shape (three typed primitives with probabilities, evaluated in parallel and in isolation) is a good abstraction for recommendation micro-decisions. Community reimplementations on Apple Silicon exist.

## Decision
Adopt the three primitives as feedlens's own `DecisionContract`. All model-derived judgments go through it. Backends are pluggable: `ollama` (default), `typesafe` (opt-in), `fake` (tests), `mlx` (future).

## Consequences
+ Ranking code is independent of any vendor; Jev can be benchmarked against local models with zero code change.
+ Cache and calibration are uniform across backends.
− We reimplement probability extraction for local models (logprobs) and must calibrate ourselves.
