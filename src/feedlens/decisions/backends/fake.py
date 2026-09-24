"""Deterministic backend for tests (spec 001)."""

from __future__ import annotations

import hashlib

from feedlens.decisions.contract import (
    AnswerMeta,
    Answers,
    BackendCapabilities,
    Choice,
    ChoiceAnswer,
    Noul,
    NoulAnswer,
    Question,
    Score,
    ScoreAnswer,
    State,
)


def _unit(seed: str) -> float:
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


class FakeBackend:
    id = "fake"
    capabilities = BackendCapabilities(supports_logprobs=True, supports_batch_state=True)

    async def evaluate(self, state: State, questions: dict[str, Question]) -> Answers:
        key = state if isinstance(state, str) else repr(sorted(state.items()))
        out: Answers = {}
        meta = AnswerMeta(method="fake")
        for name, q in questions.items():
            if isinstance(q, Noul):
                out[name] = NoulAnswer(p=_unit(f"{key}|{name}"), meta=meta)
            elif isinstance(q, Choice):
                raw = {k: _unit(f"{key}|{name}|{k}") for k in q.criteria}
                total = sum(raw.values())
                out[name] = ChoiceAnswer.from_probs({k: v / total for k, v in raw.items()}, meta)
            elif isinstance(q, Score):
                raw = [_unit(f"{key}|{name}|{i}") for i in range(len(q.criteria))]
                total = sum(raw)
                out[name] = ScoreAnswer.from_probs([v / total for v in raw], meta)
        return out

    async def evaluate_many(self, states: list[State], questions: dict[str, Question]) -> list[Answers]:
        return [await self.evaluate(s, questions) for s in states]
