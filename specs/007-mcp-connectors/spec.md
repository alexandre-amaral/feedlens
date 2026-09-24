# Spec 007 — MCP client connectors

**Status:** approved · **Phase:** 3 · **Depends on:** 002

## Why

MCP servers already exist for several sources (Readwise Reader official hosted MCP, Karakeep official `@karakeep/mcp`, Podcast Index community servers, GDELT servers, Hardcover, Trakt). Consuming them lets feedlens add sources without writing bespoke API clients, and lets users bring their own servers. feedlens **consumes** MCP in the MVP; exposing feedlens itself as an MCP server is v2 (ADR-0008).

## Design

- Uses the official `mcp` Python SDK client (stdio and streamable-HTTP transports).
- A source of kind `mcp` has `config = {transport: "stdio"|"http", command/args/env | url, headers, mapping}`.
- `mapping` declares how to turn tool results into items/signals:
  ```json
  {
    "list_tool": {"name": "list_documents", "args": {"location": "new", "limit": 100}, "cursor_arg": "updated_after"},
    "item": {"path": "$.results[*]", "url": "$.url", "title": "$.title", "text": "$.summary", "published_at": "$.saved_at", "kind": "article"},
    "signal": {"when": "$.location == 'archive'", "kind": "read"}
  }
  ```
  JSONPath via `jsonpath-ng`. Mapping presets ship for: `readwise`, `karakeep`, `podcastindex` (trending/search by category), `gdelt` (doc search by query).
- Auth: bearer tokens/env vars stored in `~/.feedlens/secrets.json` (0600), referenced as `${SECRET_NAME}` in config.
- Tool discovery UI: after adding a server, list its tools and let the user pick `list_tool` and map fields with a small form pre-filled by the preset.
- Safety: MCP tool results are data; feedlens never executes instructions found in content. Rate-limit per server (1 call/s default).

## Acceptance criteria

- AC-1 Adding the Readwise hosted MCP (`https://mcp2.readwise.io/mcp`) with the preset pulls saved documents as articles and archive as `read` signals.
- AC-2 A local Karakeep MCP via stdio (`npx @karakeep/mcp`) pulls bookmarks with tags into `metadata.tags`.
- AC-3 Podcast Index preset pulls trending episodes for chosen categories as `podcast` items.
- AC-4 A malformed mapping fails validation with a message pointing at the offending JSONPath.

## Open questions

- Should feedlens ship a generic "LLM-assisted mapping" that inspects a tool's schema and proposes a mapping? Nice-to-have, v0.2.
