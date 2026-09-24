# Discovery decisions (2026-09-24)

Answers given by the maintainer during discovery; these fixed the scope encoded in the specs.

| Question | Decision |
|---|---|
| MVP sources | YouTube (Takeout + subs/likes + channel RSS), articles (RSS / Karakeep / Readwise), podcasts via RSS, news with bias (GDELT + MBFC instead of Ground News) |
| Role of Jev | Contract as central interface; backend pluggable; local SLM default, Jev optional |
| Deployment | Local on a MacBook, as light as possible, hot refresh |
| Users | Single user for v1, public open-source from day one |
| Stack | Python (FastAPI + SQLite/sqlite-vec) + light TS SPA (Vite + Preact) |
| Ingestion | Own minimal (RSS + Takeout + OPML); readers via MCP/OPML, never hard deps |
| Hot refresh | On-demand + background scheduler + instant re-rank from cached decisions |
| Controls | Deterministic rules, editable weights/thresholds, NL profile, per-item feedback |
| Models | Ollama: Qwen3.5-4B (decisions), Qwen3-Embedding-0.6B (embeddings) |
| MCP | App consumes MCP servers as connectors; exposing an MCP server deferred |
| Language | English everywhere; UI i18n en/pt-BR |
| License / repo | MIT, GitHub public `<github-user>/feedlens`, single author |
| Handoff | Spec-kit style: constitution, specs/, plans/, tasks/ + ADRs + AGENTS.md; Claude Code does git init/push |
| MVP success | Replace YouTube home + RSS reader for two weeks of daily use |
