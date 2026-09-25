# feedlens

**Your feed, your algorithm.** A self-hosted, open-source recommendation engine for the content you already consume — YouTube, RSS articles, podcasts, news — where every ranking decision is typed, calibrated, explainable and editable by you.

feedlens runs locally on a laptop (Apple Silicon first), uses small local models through Ollama, and never sends your history anywhere unless you plug in an external decision backend on purpose.

## Why

Platform feeds optimize for the platform. feedlens inverts that: you write the policy ("more long-form engineering talks, less drama, never clickbait, surface what my subscriptions posted this week"), the engine turns every candidate into a set of **typed decisions with calibrated probabilities**, and the final score is a transparent formula whose weights you own. Every card shows *why* it is there.

## How it works (one paragraph)

Connectors pull candidates and signals (RSS/YouTube channel feeds, Google Takeout watch history, OPML, MCP servers such as Readwise or Podcast Index, GDELT + MBFC for news bias). Items are normalized, embedded (Qwen3-Embedding) and stored in SQLite + sqlite-vec. Hybrid retrieval builds a pool of ~200 candidates. Each candidate is evaluated **pointwise** through the **Decision Contract** — Noul (yes/no), Choice (one of N), Score (ordinal) questions — by a pluggable backend (local Ollama by default; TypeSafe Jev optional). Decisions are cached per item, so changing rules, weights or the natural-language profile re-ranks instantly. A calibrated re-rank keeps the feed's category mix close to yours, with an exploration slot. Your feedback (👍 👎 "less of this" "why?") refits per-field calibration and score weights.

## Status

Discovery complete; specifications and implementation plan are in this repository. Implementation has not started. See [HANDOFF.md](HANDOFF.md).

## Repository map

| Path | What |
|---|---|
| `HANDOFF.md` | Start here — how to execute this repo with a coding agent |
| `AGENTS.md` | Rules for coding agents (Claude Code, Hermes, Codex) |
| `.specify/memory/constitution.md` | Non-negotiable principles (spec-kit constitution) |
| `specs/` | Feature specifications (what & why, acceptance criteria) |
| `plans/` | Implementation plan, phases, milestones |
| `tasks/` | Ordered, dependency-aware task list for the MVP |
| `docs/ARCHITECTURE.md` | System architecture and data flow |
| `docs/DATA_MODEL.md` | SQLite schema and entity definitions |
| `docs/adr/` | Architecture Decision Records |
| `docs/research/` | Discovery research (sources, feasibility, model landscape) |
| `src/feedlens/` | Python package skeleton (contracts, interfaces, schema) |
| `web/` | Vite + Preact SPA (skeleton) |

## Quick start (target — not yet functional)

```bash
brew install ollama uv
brew services start ollama          # or: ollama serve
ollama pull qwen3.5:4b && ollama pull qwen3-embedding:0.6b
git clone https://github.com/alexandre-amaral/feedlens.git && cd feedlens
uv sync
cp .env.example .env
uv run feedlens init          # creates ~/.feedlens/feedlens.db
uv run feedlens import takeout ~/Downloads/Takeout/YouTube/history/watch-history.json
uv run feedlens sources add opml ~/subscriptions.opml
uv run feedlens refresh       # pull → embed → decide → rank
uv run feedlens serve         # http://127.0.0.1:8765
```

## License

MIT — see [LICENSE](LICENSE).
