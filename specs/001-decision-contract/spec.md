# Spec 001 — Decision Contract

**Status:** approved · **Owner:** maintainer · **Phase:** 0 · **Depends on:** —

## Why

Every model-derived judgment in feedlens must be typed, probabilistic, pointwise and backend-agnostic. This is the "JEV-based" core: the same three primitives TypeSafe's Jev exposes (Noul, Choice, Score), so that a local SLM, a classical classifier or the Jev API can be swapped without touching ranking code. (ADR-0001, ADR-0006)

## Scope

- Pydantic models for questions and answers.
- `DecisionBackend` protocol with `evaluate(state, questions) -> Answers`, `id`, `capabilities` (supports_logprobs, supports_batch_state, max_state_tokens).
- Backends: `fake` (deterministic, for tests), `ollama` (default), `typesafe` (opt-in, thin wrapper over `typesafe-sdk`; must import lazily so the dependency is optional).
- Question set registry: `QuestionSet(version, questions)`; MVP set `v1` defined in `feedlens/decisions/questions.py`.
- Cache layer keyed by `(item_id, question_set_version, backend_id)` with `state_hash` invalidation.

## Functional requirements

- FR-1 `Noul` returns `p ∈ [0,1]`; `Choice` returns `choice`, `probabilities` summing to 1 ± 1e-6, `confidence = (n·max_p − 1)/(n − 1)`; `Score` returns `score` = Σ level_index·p, `probabilities`, `confidence`.
- FR-2 Every answer carries `calibrated: bool` and `raw: dict` (untouched backend output) for auditing.
- FR-3 Ollama backend: builds one prompt per item; requests JSON via `format` schema where the only allowed values are the labels; when the runtime returns `logprobs`, derive the distribution from label-token logprobs; otherwise ask the model to output a distribution and flag `calibrated=False`, `method="verbalized"`.
- FR-4 Concurrency: backend calls are async with a semaphore (default 4). Retries with exponential backoff on 429/5xx/timeouts, max 3.
- FR-5 State budget: raise `StateTooLarge` if the rendered state exceeds `capabilities.max_state_tokens` (default 4,000 for Ollama).
- FR-6 Batch API: `evaluate_many(states: list, questions) -> list[Answers]` with per-item isolation guaranteed (no cross-item context in a single prompt).
- FR-7 Cache: `DecisionCache.get_or_evaluate(item, question_set, backend)`; hit rate exposed in `/api/stats`.

## Acceptance criteria

- AC-1 `pytest tests/decisions` passes with `fake` backend, covering FR-1 math and FR-2 fields.
- AC-2 With Ollama running `qwen3.5:4b`, `feedlens decide --item <id>` prints answers for the `v1` question set in < 2 s per item on M1 Air (median over 20 items).
- AC-3 Swapping `FEEDLENS_DECISION_BACKEND=fake|ollama|typesafe` requires no code change; missing `typesafe-sdk` yields a clear error only when that backend is selected.
- AC-4 Evaluating the same item twice hits the cache; changing the profile text changes `state_hash` and re-evaluates.

## Open questions

- Should `Choice` support multi-label (top-k topics)? MVP: single label; store full distribution so the UI can show the top-3.
- Ollama logprobs on the MLX runner: verify availability on ≥ 0.33; if absent, fall back per FR-3.
