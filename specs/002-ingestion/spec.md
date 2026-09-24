# Spec 002 — Ingestion & connectors

**Status:** approved · **Phase:** 1 · **Depends on:** 001 (types only), store

## Why

The feed is only as good as its candidates and signals. Platforms restrict APIs (YouTube watch history unavailable since 2016; Spotify capped; Ground News has no API), so ingestion is **export-first + open feeds**, with MCP servers as an extension point. (ADR-0004, ADR-0008)

## Scope (MVP)

| Connector | Input | Produces |
|---|---|---|
| `rss` | feed URL | Items (article or podcast when enclosure is audio) |
| `youtube_rss` | channel_id / channel URL / handle | Items kind=video (title, description, published, thumbnail, video_id) |
| `opml` | file | creates `rss` / `youtube_rss` sources |
| `takeout` | `watch-history.json` (My Activity JSON) | Signals kind=watched with `occurred_at`, plus stub Items for unseen videos (title + url, text empty) |
| `mcp` | server spec `{command, args, env}` or `{url}` + tool mapping | Items/Signals through a generic adapter (see 007) |
| `news_bias` | GDELT DOC 2.0 query list + MBFC table | Items kind=news with `metadata.bias`, `metadata.factuality`, `metadata.outlet` |

Out of MVP: `youtube_oauth` (subscriptions/likes; Phase 3), Spotify, Trakt, Hardcover.

## Functional requirements

- FR-1 Connector interface: `pull(since: datetime | None) -> AsyncIterator[RawItem | RawSignal]`; connectors are stateless, cursor stored in `sources.last_pulled_at`.
- FR-2 Canonicalization: URL normalization (strip tracking params, `youtu.be` → `watch?v=`), `url_hash = sha256(canonical_url)`; upsert keeps the earliest `published_at` and the longest `text`.
- FR-3 Language detection on title+text (fast heuristic lib); store ISO code.
- FR-4 Rate limiting per host (default 2 req/s) and conditional GET (ETag/Last-Modified) for RSS.
- FR-5 Takeout parser handles both JSON and HTML exports; ignores ads (`details.name == "From Google Ads"`); maps `titleUrl` to video id; imports ≥ 50k entries in < 60 s.
- FR-6 OPML import creates sources idempotently; YouTube OPML (from `youtube.com/subscription_manager`-style exports or third-party) recognized by `xmlUrl` pattern.
- FR-7 CLI: `feedlens sources add rss <url>`, `sources add youtube <channel>`, `sources add opml <file>`, `import takeout <file>`, `sources list`, `sources pull [--source id]`.
- FR-8 Failures are per-source, logged, never abort the refresh.

## Acceptance criteria

- AC-1 Importing a real Takeout file yields signals; `feedlens stats` shows count by month.
- AC-2 Adding 50 YouTube channels + 30 RSS feeds and pulling completes in < 90 s cold on a normal connection.
- AC-3 Duplicate items across feeds (same canonical URL) produce one row.
- AC-4 Unit tests with fixture feeds (RSS 2.0, Atom, podcast enclosure, YouTube XML, Takeout JSON sample) pass offline.

## Open questions

- Transcripts for YouTube videos (yt-dlp/`youtube-transcript-api`) would improve decisions but add cost/ToS risk. MVP: no; revisit after two-week trial.
- Full-text extraction for articles (readability): MVP uses feed summary only; task T-2.9 evaluates `trafilatura` as optional.
