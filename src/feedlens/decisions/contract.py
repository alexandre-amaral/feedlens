"""The Decision Contract — feedlens's central interface (spec 001, ADR-0001).

Three typed primitives, evaluated pointwise and independently against a `state`:

* Noul   — yes/no → probability
* Choice — one of N labels → distribution + confidence
* Score  — ordinal levels → probability-weighted score + distribution + confidence

Every backend (fake, ollama, typesafe, mlx) implements `DecisionBackend`.
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field, model_validator

# --------------------------------------------------------------------------- questions


class Noul(BaseModel):
    type: Literal["noul"] = "noul"
    instructions: str
    criteria: dict[Literal["true", "false"], str] | None = None


class Choice(BaseModel):
    type: Literal["choice"] = "choice"
    instructions: str
    criteria: dict[str, str] = Field(min_length=2, max_length=255)


class Score(BaseModel):
    type: Literal["score"] = "score"
    instructions: str
    criteria: list[str] = Field(min_length=2, max_length=10)


Question = Noul | Choice | Score


class QuestionSet(BaseModel):
    version: str
    questions: dict[str, Question]


# --------------------------------------------------------------------------- answers


def confidence_from_probs(probs: list[float]) -> float:
    """Concentration statistic used by Jev: (n·max_p − 1) / (n − 1); 1.0 for n == 1."""
    n = len(probs)
    if n <= 1:
        return 1.0
    return (n * max(probs) - 1.0) / (n - 1.0)


class AnswerMeta(BaseModel):
    calibrated: bool = False
    method: Literal["logprobs", "verbalized", "backend", "fake"] = "fake"
    raw: dict[str, object] = Field(default_factory=dict)


class NoulAnswer(BaseModel):
    type: Literal["noul"] = "noul"
    p: float = Field(ge=0.0, le=1.0)
    meta: AnswerMeta = Field(default_factory=AnswerMeta)


class ChoiceAnswer(BaseModel):
    type: Literal["choice"] = "choice"
    choice: str
    probabilities: dict[str, float]
    confidence: float
    meta: AnswerMeta = Field(default_factory=AnswerMeta)

    @model_validator(mode="after")
    def _check(self) -> ChoiceAnswer:
        total = sum(self.probabilities.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"probabilities must sum to 1, got {total}")
        if self.choice not in self.probabilities:
            raise ValueError("choice must be one of the probability keys")
        return self

    @classmethod
    def from_probs(
        cls, probabilities: dict[str, float], meta: AnswerMeta | None = None
    ) -> ChoiceAnswer:
        choice = max(probabilities, key=probabilities.__getitem__)
        return cls(
            choice=choice,
            probabilities=probabilities,
            confidence=confidence_from_probs(list(probabilities.values())),
            meta=meta or AnswerMeta(),
        )


class ScoreAnswer(BaseModel):
    type: Literal["score"] = "score"
    score: float
    probabilities: list[float]
    confidence: float
    meta: AnswerMeta = Field(default_factory=AnswerMeta)

    @model_validator(mode="after")
    def _check(self) -> ScoreAnswer:
        total = sum(self.probabilities)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"probabilities must sum to 1, got {total}")
        expected = sum(i * p for i, p in enumerate(self.probabilities))
        if abs(expected - self.score) > 1e-6:
            raise ValueError("score must equal the probability-weighted level index")
        return self

    @classmethod
    def from_probs(cls, probabilities: list[float], meta: AnswerMeta | None = None) -> ScoreAnswer:
        return cls(
            score=sum(i * p for i, p in enumerate(probabilities)),
            probabilities=probabilities,
            confidence=confidence_from_probs(probabilities),
            meta=meta or AnswerMeta(),
        )


Answer = NoulAnswer | ChoiceAnswer | ScoreAnswer
Answers = dict[str, Answer]

State = str | dict[str, object]


# --------------------------------------------------------------------------- backend


class BackendCapabilities(BaseModel):
    supports_logprobs: bool = False
    supports_batch_state: bool = False  # true only when items are isolated (Jev-style arrays)
    max_state_tokens: int = 4000


class StateTooLarge(ValueError):
    pass


@runtime_checkable
class DecisionBackend(Protocol):
    id: str
    capabilities: BackendCapabilities

    async def evaluate(self, state: State, questions: dict[str, Question]) -> Answers: ...

    async def evaluate_many(
        self, states: list[State], questions: dict[str, Question]
    ) -> list[Answers]: ...
