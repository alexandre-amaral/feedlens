import pytest

from feedlens.models import Item, Profile


def test_profile_defaults() -> None:
    p = Profile()
    assert p.text == "" and p.topics == [] and p.avoid == [] and p.depth_pref == 2


def test_profile_depth_pref_bounds() -> None:
    with pytest.raises(ValueError):
        Profile(depth_pref=4)


def test_item_kind_is_constrained() -> None:
    with pytest.raises(ValueError):
        Item(id="i", url_hash="h", kind="tweet", url="u", title="t", created_at="c")  # type: ignore[arg-type]
