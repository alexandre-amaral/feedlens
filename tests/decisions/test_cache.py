from pathlib import Path

from feedlens.decisions.backends.fake import FakeBackend
from feedlens.decisions.cache import DecisionCache
from feedlens.decisions.contract import Answers, Question, State
from feedlens.decisions.questions import question_set_v1
from feedlens.models import Item, Profile
from feedlens.store.db import connect, migrate


class CountingBackend(FakeBackend):
    def __init__(self) -> None:
        self.calls = 0

    async def evaluate(self, state: State, questions: dict[str, Question]) -> Answers:
        self.calls += 1
        return await super().evaluate(state, questions)


def _item(i: str) -> Item:
    return Item(
        id=i, url_hash=f"h{i}", kind="article", url=f"https://x/{i}", title=f"T{i}", created_at="c"
    )


def _db(tmp_path: Path):  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "t.db")
    migrate(conn)
    for i in ("a", "b", "c"):
        conn.execute(
            "insert into items(id,url_hash,kind,url,title,created_at) values (?,?,?,?,?,?)",
            (i, f"h{i}", "article", f"https://x/{i}", f"T{i}", "c"),
        )
    return conn


async def test_second_call_hits_cache(tmp_path: Path) -> None:
    backend = CountingBackend()
    cache = DecisionCache(_db(tmp_path), question_set_v1(), backend)
    p = Profile(text="rust")
    first = await cache.get_or_evaluate(_item("a"), p)
    second = await cache.get_or_evaluate(_item("a"), p)
    assert first == second
    assert backend.calls == 1
    assert (cache.hits, cache.misses) == (1, 1)


async def test_profile_change_invalidates_and_replaces_row(tmp_path: Path) -> None:
    conn = _db(tmp_path)
    backend = CountingBackend()
    cache = DecisionCache(conn, question_set_v1(), backend)
    await cache.get_or_evaluate(_item("a"), Profile(text="rust"))
    await cache.get_or_evaluate(_item("a"), Profile(text="python"))
    assert backend.calls == 2
    rows = conn.execute("select state_hash from decisions where item_id='a'").fetchall()
    assert len(rows) == 1  # replaced, not duplicated (PK item, version, backend)


async def test_many_evaluates_only_missing(tmp_path: Path) -> None:
    backend = CountingBackend()
    cache = DecisionCache(_db(tmp_path), question_set_v1(), backend)
    p = Profile()
    await cache.get_or_evaluate(_item("b"), p)
    out = await cache.get_or_evaluate_many([_item("a"), _item("b"), _item("c")], p)
    assert [set(o) for o in out] == [set(question_set_v1().questions)] * 3
    assert backend.calls == 3  # b was cached; a and c evaluated
    assert out[1] == await cache.get_or_evaluate(_item("b"), p)


async def test_cache_key_includes_backend_id(tmp_path: Path) -> None:
    conn = _db(tmp_path)
    b1, b2 = CountingBackend(), CountingBackend()
    b2.id = "fake-2"
    await DecisionCache(conn, question_set_v1(), b1).get_or_evaluate(_item("a"), Profile())
    await DecisionCache(conn, question_set_v1(), b2).get_or_evaluate(_item("a"), Profile())
    assert (b1.calls, b2.calls) == (1, 1)
    assert conn.execute("select count(*) from decisions").fetchone()[0] == 2
