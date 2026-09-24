import pytest

from feedlens.decisions.backends.fake import FakeBackend
from feedlens.decisions.contract import ChoiceAnswer, ScoreAnswer, confidence_from_probs
from feedlens.decisions.questions import question_set_v1


def test_confidence_formula():
    assert confidence_from_probs([1.0, 0.0, 0.0]) == pytest.approx(1.0)
    assert confidence_from_probs([1 / 3, 1 / 3, 1 / 3]) == pytest.approx(0.0)
    assert confidence_from_probs([0.6, 0.4]) == pytest.approx(0.2)


def test_score_is_weighted_mean():
    a = ScoreAnswer.from_probs([0.0, 0.57, 0.43])
    assert a.score == pytest.approx(1.43)


def test_choice_picks_argmax_and_validates():
    a = ChoiceAnswer.from_probs({"a": 0.2, "b": 0.8})
    assert a.choice == "b"
    with pytest.raises(ValueError):
        ChoiceAnswer(choice="a", probabilities={"a": 0.5, "b": 0.6}, confidence=0.1)


async def test_fake_backend_is_deterministic_and_complete():
    qs = question_set_v1()
    b = FakeBackend()
    a1 = await b.evaluate("profile: x\nitem: y", qs.questions)
    a2 = await b.evaluate("profile: x\nitem: y", qs.questions)
    assert a1 == a2
    assert set(a1) == set(qs.questions)
    assert 0.0 <= a1["clickbait"].p <= 1.0  # type: ignore[union-attr]
