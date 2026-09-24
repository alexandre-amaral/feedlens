"""Backend selection by settings (spec 001 AC-3): fake | ollama | typesafe, no code change."""

from __future__ import annotations

from feedlens.config import Settings
from feedlens.decisions.contract import DecisionBackend


def get_backend(settings: Settings) -> DecisionBackend:
    if settings.decision_backend == "fake":
        from feedlens.decisions.backends.fake import FakeBackend

        return FakeBackend()
    if settings.decision_backend == "ollama":
        from feedlens.decisions.backends.ollama import OllamaBackend

        return OllamaBackend(
            base_url=settings.ollama_url,
            model=settings.decision_model,
            concurrency=settings.decision_concurrency,
        )
    if settings.decision_backend == "typesafe":
        from feedlens.decisions.backends.typesafe import TypeSafeBackend

        return TypeSafeBackend()
    raise ValueError(f"unknown decision backend: {settings.decision_backend}")
