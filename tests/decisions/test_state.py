import pytest

from feedlens.decisions.contract import Choice, Noul, Score, StateTooLarge
from feedlens.decisions.questions import get_question_set, question_set_v1
from feedlens.decisions.state import (
    PROFILE_TOKEN_BUDGET,
    estimate_tokens,
    render_state,
    state_hash,
)
from feedlens.models import Item, Profile, Topic


def _item(**kw: object) -> Item:
    base: dict[str, object] = {
        "id": "01J",
        "url_hash": "h",
        "kind": "video",
        "url": "https://www.youtube.com/watch?v=abc",
        "title": "Rust async deep dive",
        "text": "tokio internals explained",
        "author": "Jon",
        "published_at": "2026-09-20T10:00:00Z",
        "duration_s": 3600,
        "language": "en",
        "created_at": "2026-09-24T00:00:00Z",
    }
    base.update(kw)
    return Item(**base)  # type: ignore[arg-type]


def test_question_set_v1_shape() -> None:
    qs = question_set_v1()
    assert qs.version == "v1"
    assert set(qs.questions) == {"topics", "fit", "depth", "clickbait", "novelty", "avoid"}
    assert isinstance(qs.questions["topics"], Choice)
    assert isinstance(qs.questions["fit"], Score) and len(qs.questions["fit"].criteria) == 5
    assert isinstance(qs.questions["depth"], Score) and len(qs.questions["depth"].criteria) == 4
    for n in ("clickbait", "novelty", "avoid"):
        assert isinstance(qs.questions[n], Noul)


def test_question_set_registry_uses_profile_topics() -> None:
    p = Profile(
        topics=[Topic(label="rust", description="Rust lang"), Topic(label="x", description="y")]
    )
    qs = get_question_set("v1", profile=p)
    topics = qs.questions["topics"]
    assert isinstance(topics, Choice)
    assert set(topics.criteria) == {"rust", "x"}
    with pytest.raises(KeyError):
        get_question_set("v99")


def test_render_state_has_profile_and_item_blocks() -> None:
    p = Profile(text="More long-form engineering talks.", avoid=["drama"], depth_pref=3)
    s = render_state(p, _item())
    assert s.startswith("profile:")
    assert "More long-form engineering talks." in s
    assert "avoid: drama" in s
    assert "depth_pref: 3" in s
    assert "\nitem:" in s
    for frag in (
        "kind: video",
        "title: Rust async deep dive",
        "author: Jon",
        "duration: 60 min",
        "language: en",
        "text: tokio internals explained",
    ):
        assert frag in s, frag


def test_render_state_omits_missing_item_fields() -> None:
    s = render_state(Profile(), _item(author=None, duration_s=None, language=None, text=""))
    assert "author:" not in s
    assert "duration:" not in s
    assert "language:" not in s
    assert "text:" not in s


def test_estimate_tokens_is_chars_over_four_rounded_up() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcde") == 2


def test_render_state_truncates_item_text_to_budget() -> None:
    long_text = "word " * 5000  # ~6k tokens
    s = render_state(Profile(text="short"), _item(text=long_text), max_tokens=500)
    assert estimate_tokens(s) <= 500
    assert "title: Rust async deep dive" in s  # title survives, text is what gets cut


def test_render_state_raises_when_profile_alone_exceeds_budget() -> None:
    huge = "x" * (PROFILE_TOKEN_BUDGET * 4 + 40)
    with pytest.raises(StateTooLarge):
        render_state(Profile(text=huge), _item())
    with pytest.raises(StateTooLarge):
        render_state(Profile(text="ok"), _item(text=""), max_tokens=5)


def test_state_hash_tracks_profile_and_version_only() -> None:
    qs = question_set_v1()
    p = Profile(text="a")
    assert state_hash(p, qs) == state_hash(Profile(text="a"), qs)
    assert state_hash(p, qs) != state_hash(Profile(text="b"), qs)
    assert state_hash(p, qs) != state_hash(Profile(text="a", avoid=["z"]), qs)
    assert state_hash(p, qs) != state_hash(p, qs.model_copy(update={"version": "v2"}))
    assert len(state_hash(p, qs)) == 64


def test_single_topic_profile_still_yields_a_valid_choice() -> None:
    p = Profile(topics=[Topic(label="rust", description="Rust lang")])
    qs = get_question_set("v1", profile=p)
    topics = qs.questions["topics"]
    assert isinstance(topics, Choice)
    assert "rust" in topics.criteria
    assert "other" in topics.criteria  # escape label added so Choice has >= 2 options


def test_state_hash_tracks_question_set_content() -> None:
    p1 = Profile(topics=[Topic(label="a", description="one"), Topic(label="b", description="two")])
    p2 = Profile(
        topics=[Topic(label="a", description="CHANGED"), Topic(label="b", description="two")]
    )
    assert state_hash(p1, get_question_set("v1", p1)) != state_hash(p2, get_question_set("v1", p2))
