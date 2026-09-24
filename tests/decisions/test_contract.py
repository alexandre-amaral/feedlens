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


# --- FR-2 audit fields, validation bounds, FR-6 isolation (T-0.4) ---


async def test_every_answer_carries_calibrated_and_raw() -> None:
    qs = question_set_v1()
    answers = await FakeBackend().evaluate("profile: x\nitem: y", qs.questions)
    for name, a in answers.items():
        assert a.meta.calibrated is False, name
        assert isinstance(a.meta.raw, dict), name
        assert a.meta.method == "fake"


def test_noul_answer_bounds() -> None:
    from feedlens.decisions.contract import NoulAnswer

    with pytest.raises(ValueError):
        NoulAnswer(p=1.5)
    with pytest.raises(ValueError):
        NoulAnswer(p=-0.1)


def test_choice_criteria_limits() -> None:
    from feedlens.decisions.contract import Choice

    with pytest.raises(ValueError):
        Choice(instructions="x", criteria={"only": "one"})
    too_many = {f"l{i}": "d" for i in range(256)}
    with pytest.raises(ValueError):
        Choice(instructions="x", criteria=too_many)
    assert len(Choice(instructions="x", criteria={"a": "1", "b": "2"}).criteria) == 2


def test_score_level_limits() -> None:
    from feedlens.decisions.contract import Score

    with pytest.raises(ValueError):
        Score(instructions="x", criteria=["one"])
    with pytest.raises(ValueError):
        Score(instructions="x", criteria=[str(i) for i in range(11)])
    assert len(Score(instructions="x", criteria=[str(i) for i in range(10)]).criteria) == 10


async def test_evaluate_many_is_pointwise_isolated() -> None:
    qs = question_set_v1()
    b = FakeBackend()
    states = ["profile: x\nitem: a", "profile: x\nitem: b", "profile: x\nitem: c"]
    many = await b.evaluate_many(states, qs.questions)
    assert len(many) == 3
    for s, ans in zip(states, many, strict=True):
        assert ans == await b.evaluate(s, qs.questions)
    # order of neighbours must not change an item's answers
    assert (await b.evaluate_many(states[::-1], qs.questions))[::-1] == many
