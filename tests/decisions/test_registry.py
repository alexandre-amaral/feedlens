import pytest

from feedlens.config import Settings
from feedlens.decisions.backends.fake import FakeBackend
from feedlens.decisions.backends.ollama import OllamaBackend
from feedlens.decisions.contract import DecisionBackend
from feedlens.decisions.registry import get_backend


def test_fake_backend_selected_by_settings() -> None:
    b = get_backend(Settings(decision_backend="fake"))
    assert isinstance(b, FakeBackend)
    assert isinstance(b, DecisionBackend)
    assert b.id == "fake"


def test_ollama_backend_carries_model_in_id() -> None:
    s = Settings(decision_backend="ollama", decision_model="qwen3.5:4b", decision_concurrency=2)
    b = get_backend(s)
    assert isinstance(b, OllamaBackend)
    assert b.id == "ollama:qwen3.5:4b"
    assert b.base_url == s.ollama_url
    assert b.concurrency == 2


def test_typesafe_without_sdk_is_a_clear_error() -> None:
    with pytest.raises(RuntimeError, match="--extra typesafe"):
        get_backend(Settings(decision_backend="typesafe"))
