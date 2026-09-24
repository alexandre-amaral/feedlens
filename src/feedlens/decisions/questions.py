"""Question set v1 — the MVP per-item decisions (spec 001, docs/ARCHITECTURE.md)."""

from feedlens.decisions.contract import Choice, Noul, QuestionSet, Score

DEFAULT_TOPICS: dict[str, str] = {
    "ai-engineering": "Building with LLMs, agents, ML systems, data engineering",
    "software-engineering": "Programming, architecture, tooling, developer practices",
    "science": "Research, physics, biology, mathematics explained",
    "business-tech": "Startups, product, industry analysis",
    "world-news": "Politics, economy, international events",
    "entertainment": "Film, series, games, music commentary",
    "lifestyle": "Health, fitness, productivity, hobbies",
    "other": "Does not fit any of the above",
}


def question_set_v1(topics: dict[str, str] | None = None) -> QuestionSet:
    return QuestionSet(
        version="v1",
        questions={
            "topics": Choice(
                instructions="Which single topic best describes this item?",
                criteria=topics or DEFAULT_TOPICS,
            ),
            "fit": Score(
                instructions="How well does this item match what the profile asks for right now?",
                criteria=[
                    "Irrelevant to the profile",
                    "Loosely related",
                    "Relevant",
                    "Strong match",
                    "Exactly what the profile asks for",
                ],
            ),
            "depth": Score(
                instructions="How deep or long-form is the content?",
                criteria=["Shallow or promotional", "Light overview", "Substantive", "Deep, long-form or technical"],
            ),
            "clickbait": Noul(
                instructions="The title or description uses clickbait, outrage or manipulative framing.",
            ),
            "novelty": Noul(
                instructions="The item says something the profile suggests the user has not seen recently.",
            ),
            "avoid": Noul(
                instructions="The item matches any entry in the profile's avoid list.",
            ),
        },
    )
