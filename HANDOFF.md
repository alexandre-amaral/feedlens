# HANDOFF — feedlens

This repository is the output of a discovery session (2026-09-24). It contains everything a coding agent or a contributor needs to start implementing: constitution, specs, plan, tasks, ADRs, architecture, data model and a package skeleton. No feature code exists yet.

## 0. First actions on the developer's machine

```bash
# 1. Initialize git with the sole author
cd feedlens
git init -b main
git config user.name  "Alexandre Amaral"
git config user.email "alexandre.samaral@protonmail.com"
git add -A
git commit -m "chore: bootstrap feedlens with discovery, specs, plan and skeleton"

# 2. Create the public repository (replace alexandre-amaral)
gh repo create alexandre-amaral/feedlens --public --source=. --push \
  --description "Your feed, your algorithm. Self-hosted, explainable, calibrated recommendations for what you already consume."

# 3. Replace the placeholder everywhere
grep -rl "alexandre-amaral" . | xargs sed -i '' 's/alexandre-amaral/YOUR_HANDLE/g'
git commit -am "chore: set repository owner"
git push
```

Commit policy: **single author, no co-author trailers, no agent attribution lines** in commit messages or PR bodies. Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).

## 1. Reading order

1. `.specify/memory/constitution.md` — the rules that override everything else.
2. `docs/ARCHITECTURE.md` — the shape of the system.
3. `specs/001-decision-contract/spec.md` — the central interface; everything depends on it.
4. `plans/mvp-plan.md` — phases and milestones.
5. `tasks/mvp-tasks.md` — the executable backlog. Work top-down; respect `depends_on`.
6. `docs/adr/` — when you wonder "why not X", the answer is probably there.

## 2. Definition of the MVP

Success criterion agreed in discovery: **the developer replaces the YouTube home page and his RSS reader with feedlens for two consecutive weeks of daily use.**

Scope in: YouTube (Takeout watch history + channel RSS + subscriptions/likes via OAuth in a later task), RSS articles, podcast RSS, news with bias metadata (GDELT + MBFC), MCP client connectors (Readwise, Karakeep, Podcast Index, GDELT). Single user. Local only. Ollama backend. Web SPA. Feedback loop. Hot refresh in all three senses (see `specs/006-hot-refresh`).

Scope out (v2+): Spotify, books, movies/series, multi-user auth, mobile, cloud deploy, TypeSafe Jev backend beyond the interface stub, MLX-native backend.

## 3. Working agreement for agents

- One task at a time from `tasks/mvp-tasks.md`; mark it done in the file in the same commit that finishes it.
- Every task that touches behavior ships with tests (`pytest`) and, for the SPA, a Vitest test where logic exists.
- Never widen scope to satisfy a spec ambiguity — record the ambiguity as a question in `specs/<id>/spec.md` under "Open questions" and pick the smallest interpretation.
- New architectural decisions require an ADR (`docs/adr/NNNN-title.md`) before the code lands.
- Keep the constitution's performance budgets: refresh of 500 new items < 5 min on an M1 Air 16 GB; instant re-rank < 200 ms for 2,000 scored items.

## 4. Environment

- macOS Apple Silicon, Python 3.12 via `uv`, Node 22 via `pnpm`, Ollama ≥ 0.33 (MLX runner with structured output).
- Models: `qwen3.5:4b` (decisions, non-thinking mode), `qwen3-embedding:0.6b` (embeddings). Optional reranker `qwen3-reranker:0.6b`.
- Data lives in `~/.feedlens/` (SQLite db, caches, exports). Nothing leaves the machine unless `FEEDLENS_DECISION_BACKEND=typesafe` is set explicitly.

## 5. Questions left open on purpose

See "Open questions" sections inside each spec. None of them blocks Phase 0–2.
