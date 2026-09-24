"""Ollama backend — default (spec 001 FR-3, ADR-0003). Implemented in task T-2.3.

Plan:
* one prompt per item: system = contract rules, user = rendered state + one question block
* request JSON via Ollama `format` (schema whose values are restricted to the labels)
* if the runtime returns `logprobs` for label tokens → distribution from logprobs (`method="logprobs"`)
* else ask for a distribution in JSON → `method="verbalized"`, `calibrated=False`
* asyncio.Semaphore(4), tenacity-style retry on 429/5xx/timeouts (max 3)
"""

from __future__ import annotations

from feedlens.decisions.contract import Answers, BackendCapabilities, Question, State


class OllamaBackend:
    id = "ollama"
    capabilities = BackendCapabilities(supports_logprobs=False, supports_batch_state=False)

    def __init__(self, base_url: str, model: str, concurrency: int = 4) -> None:
        self.base_url = base_url
        self.model = model
        self.id = f"ollama:{model}"
        self.concurrency = concurrency

    async def evaluate(self, state: State, questions: dict[str, Question]) -> Answers:
        raise NotImplementedError("T-2.3")

    async def evaluate_many(self, states: list[State], questions: dict[str, Question]) -> list[Answers]:
        raise NotImplementedError("T-2.3")
