"""Decision cache (spec 001 FR-7, AC-4; AGENTS.md rule 3).

Answers are cached in the `decisions` table keyed by `(item_id, question_set_version,
backend_id)`. `state_hash` (profile fragment + question-set version) invalidates a row when
the profile changes. Weights/rules never touch this cache — they only re-rank.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from pydantic import TypeAdapter

from feedlens.decisions.contract import Answers, DecisionBackend, QuestionSet, State
from feedlens.decisions.state import render_state, state_hash
from feedlens.models import Item, Profile

_ANSWERS = TypeAdapter(Answers)


class DecisionCache:
    def __init__(
        self,
        conn: sqlite3.Connection,
        question_set: QuestionSet,
        backend: DecisionBackend,
        *,
        max_state_tokens: int | None = None,
    ) -> None:
        self.conn = conn
        self.question_set = question_set
        self.backend = backend
        self.max_state_tokens = max_state_tokens or backend.capabilities.max_state_tokens
        self.hits = 0
        self.misses = 0

    # ----------------------------------------------------------------- lookup

    def lookup(self, item_id: str, expected_hash: str) -> Answers | None:
        row = self.conn.execute(
            "SELECT answers, state_hash FROM decisions "
            "WHERE item_id = ? AND question_set_version = ? AND backend_id = ?",
            (item_id, self.question_set.version, self.backend.id),
        ).fetchone()
        if row is None or row["state_hash"] != expected_hash:
            return None
        return _ANSWERS.validate_json(row["answers"])

    def store(self, item_id: str, answers: Answers, hash_: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO decisions"
            "(item_id, question_set_version, backend_id, answers, state_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                item_id,
                self.question_set.version,
                self.backend.id,
                _ANSWERS.dump_json(answers).decode("utf-8"),
                hash_,
                datetime.now(UTC).isoformat(timespec="seconds"),
            ),
        )

    # --------------------------------------------------------------- evaluate

    async def get_or_evaluate(self, item: Item, profile: Profile) -> Answers:
        return (await self.get_or_evaluate_many([item], profile))[0]

    async def get_or_evaluate_many(self, items: list[Item], profile: Profile) -> list[Answers]:
        hash_ = state_hash(profile, self.question_set)
        results: list[Answers | None] = []
        pending: list[int] = []
        for i, item in enumerate(items):
            cached = self.lookup(item.id, hash_)
            if cached is None:
                self.misses += 1
                pending.append(i)
            else:
                self.hits += 1
            results.append(cached)
        if pending:
            states: list[State] = [
                render_state(profile, items[i], max_tokens=self.max_state_tokens) for i in pending
            ]
            fresh = await self.backend.evaluate_many(states, self.question_set.questions)
            for i, answers in zip(pending, fresh, strict=True):
                self.store(items[i].id, answers, hash_)
                results[i] = answers
        return [r for r in results if r is not None]
