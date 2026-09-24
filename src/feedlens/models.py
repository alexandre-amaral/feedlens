"""Canonical domain models shared by store, decisions, ranking and API (docs/DATA_MODEL.md).

`Item` mirrors the `items` table; T-1.1 adds canonicalization/upsert on top of it.
`Profile` mirrors the single-row `profile` table (spec 004).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ItemKind = Literal["video", "article", "podcast", "news"]


class Topic(BaseModel):
    label: str
    description: str = ""


class Profile(BaseModel):
    text: str = ""
    topics: list[Topic] = Field(default_factory=list, max_length=40)
    avoid: list[str] = Field(default_factory=list)
    depth_pref: int = Field(default=2, ge=0, le=3)


class Item(BaseModel):
    id: str
    url_hash: str
    kind: ItemKind
    source_id: str | None = None
    url: str
    title: str
    text: str = ""
    author: str | None = None
    published_at: str | None = None
    duration_s: int | None = None
    language: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    seen_at: str | None = None
    created_at: str
