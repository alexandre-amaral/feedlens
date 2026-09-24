"""TypeSafe Jev backend — opt-in (spec 001 AC-3, ADR-0001). Implemented in task T-3.7.

Maps 1:1 to `typesafe_sdk` primitives (Noul/Choice/Score). Import the SDK lazily so the
dependency stays optional (`uv sync --extra typesafe`). Mark answers `method="backend"`;
`calibrated` reflects the vendor's claim, not an independent measurement (ADR-0006).
"""

from __future__ import annotations

from feedlens.decisions.contract import Answers, BackendCapabilities, Question, State


class TypeSafeBackend:
    id = "typesafe:jev-latest"
    capabilities = BackendCapabilities(
        supports_logprobs=False, supports_batch_state=True, max_state_tokens=32000
    )

    def __init__(self, api_key: str | None = None, model: str = "jev-latest") -> None:
        try:
            import typesafe_sdk  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Install with `uv sync --extra typesafe` to use the TypeSafe backend"
            ) from exc
        self.model = model
        self.id = f"typesafe:{model}"

    async def evaluate(self, state: State, questions: dict[str, Question]) -> Answers:
        raise NotImplementedError("T-3.7")

    async def evaluate_many(
        self, states: list[State], questions: dict[str, Question]
    ) -> list[Answers]:
        raise NotImplementedError("T-3.7")
