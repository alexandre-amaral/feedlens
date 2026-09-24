# feedlens Constitution

Version 1.0.0 — ratified 2026-09-24. Amendments require an ADR and a version bump.

## Article I — The user owns the algorithm

Every factor that influences what appears in the feed MUST be visible, editable and reversible by the user: deterministic rules, signal weights and thresholds, the natural-language profile, and the calibration fitted from feedback. There is no hidden objective. There is no engagement optimization the user did not ask for.

## Article II — Decisions are typed, calibrated and pointwise

All model-derived judgments pass through the Decision Contract (Noul, Choice, Score). Each answer carries a probability distribution and a confidence. Probabilities used for thresholds MUST be post-hoc calibrated on the user's own labeled feedback (temperature scaling or isotonic regression per field); raw softmax or verbalized probabilities are ranking signals only, never absolute truth. Each candidate is judged in isolation from other candidates.

## Article III — Local first, private by default

The default installation runs entirely on the user's machine with local models. Network egress is limited to configured content sources and localhost inference. Any remote decision backend (e.g. TypeSafe Jev) is opt-in, clearly labeled, and swappable without code changes. No telemetry, ever.

## Article IV — Explainability is a feature, not a log

Every ranked item exposes a score breakdown: each signal's raw value, weight, contribution, and the rule or profile fragment that produced it. If it cannot be explained in the UI, it cannot influence the rank.

## Article V — Export-first ingestion

Where platforms restrict APIs, feedlens prefers the user's own data exports (Google Takeout, OPML, CSV) plus open feeds (RSS, public indexes) over scraping. feedlens never violates a platform's terms of service on the user's behalf and never asks for account passwords.

## Article VI — Lightweight and fast

Targets on an Apple M1 Air, 16 GB: full refresh of 500 new items under 5 minutes; instant re-rank of 2,000 scored items under 200 ms; UI first paint under 1 s; idle memory under 500 MB excluding the inference runtime. Dependencies are added only when they remove more complexity than they bring.

## Article VII — Small, testable increments

Features ship behind a spec with acceptance criteria and tests. The MVP is defined by daily use, not by feature count. Anything not required to replace the YouTube home page and an RSS reader for two weeks is out of the MVP.

## Article VIII — Open source, MIT, single author for now

The code is MIT. Contributions follow `docs/CONTRIBUTING.md`. Until v0.1.0, the maintainer is the single author of record.
