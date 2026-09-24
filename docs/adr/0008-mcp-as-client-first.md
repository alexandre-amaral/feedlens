# ADR-0008 — feedlens consumes MCP servers as connectors; exposing an MCP server is deferred

Date: 2026-09-24 · Status: accepted

## Context
Official/community MCP servers exist for Readwise, Karakeep, Podcast Index, GDELT, Hardcover, Trakt. Exposing feedlens as a server (so assistants can query the feed) is attractive but not needed for the two-week daily-use goal.

## Decision
Ship a generic MCP client connector with JSONPath mappings and presets (spec 007). Defer the feedlens MCP server to v0.2 with a placeholder spec.

## Consequences
+ Source coverage grows without bespoke clients.
− Mapping UX must be good enough for non-developers; presets mitigate.
