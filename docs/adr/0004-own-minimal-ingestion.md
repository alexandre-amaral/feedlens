# ADR-0004 — Own minimal ingestion instead of depending on Miniflux/Karakeep

Date: 2026-09-24 · Status: accepted

## Context
Miniflux (Go, Apache 2.0) and Karakeep (AGPL, Next.js + Meilisearch) are mature but add services and, for Karakeep, a heavy stack and AGPL considerations. MVP needs RSS, YouTube channel feeds, OPML, Takeout and MCP.

## Decision
Implement ingestion in-process with `feedparser` + `httpx`; support both readers indirectly through their MCP servers or OPML export. Never make them hard dependencies.

## Consequences
+ Single process, MIT-clean, no extra containers.
− We own feed-parsing edge cases; mitigated by fixture-based tests.
