"""State renderer — the compact text a backend judges (spec 001 FR-5, AGENTS.md rule 6).

`state = profile block + item block`. The profile block is capped at 600 tokens, the whole
state at `max_tokens` (default 4,000). Item text is truncated first; if the state is still
over budget, `StateTooLarge` is raised. Tokens are estimated as ceil(chars / 4).
"""

from __future__ import annotations

import hashlib
import math

from feedlens.decisions.contract import QuestionSet, StateTooLarge
from feedlens.models import Item, Profile

PROFILE_TOKEN_BUDGET = 600
DEFAULT_STATE_TOKENS = 4000


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def render_profile(profile: Profile) -> str:
    lines = ["profile:"]
    if profile.text.strip():
        lines.append(f"  {profile.text.strip()}")
    if profile.topics:
        lines.append("  topics: " + ", ".join(t.label for t in profile.topics))
    if profile.avoid:
        lines.append("  avoid: " + "; ".join(profile.avoid))
    lines.append(f"  depth_pref: {profile.depth_pref}")
    return "\n".join(lines)


def _render_item(item: Item, text: str) -> str:
    lines = ["item:", f"  kind: {item.kind}", f"  title: {item.title}"]
    if item.author:
        lines.append(f"  author: {item.author}")
    if item.published_at:
        lines.append(f"  published: {item.published_at}")
    if item.duration_s is not None:
        lines.append(f"  duration: {round(item.duration_s / 60)} min")
    if item.language:
        lines.append(f"  language: {item.language}")
    if text:
        lines.append(f"  text: {text}")
    return "\n".join(lines)


def render_state(profile: Profile, item: Item, *, max_tokens: int = DEFAULT_STATE_TOKENS) -> str:
    profile_block = render_profile(profile)
    if estimate_tokens(profile_block) > PROFILE_TOKEN_BUDGET:
        raise StateTooLarge(
            f"profile is {estimate_tokens(profile_block)} tokens; budget {PROFILE_TOKEN_BUDGET}"
        )
    text = " ".join(item.text.split())
    state = f"{profile_block}\n{_render_item(item, text)}"
    if estimate_tokens(state) > max_tokens:
        without_text = f"{profile_block}\n{_render_item(item, '')}"
        room_chars = (max_tokens - estimate_tokens(without_text)) * 4 - len("  text: \n")
        if room_chars <= 0:
            raise StateTooLarge(
                f"state without text is {estimate_tokens(without_text)} tokens; max {max_tokens}"
            )
        state = f"{profile_block}\n{_render_item(item, text[:room_chars].rstrip())}"
    return state


def state_hash(profile: Profile, question_set: QuestionSet) -> str:
    """Cache-invalidation key: changes when the profile fragment or the question set changes."""
    payload = f"{question_set.version}\n{render_profile(profile)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
