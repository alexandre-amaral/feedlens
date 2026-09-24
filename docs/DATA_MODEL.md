# Data model (SQLite)

File: `~/.feedlens/feedlens.db`. WAL mode. Extensions: FTS5 (built-in), sqlite-vec (loaded at startup). All timestamps are UTC ISO-8601 strings. Canonical schema lives in `src/feedlens/store/migrations/0001_init.sql`.

## Tables

### sources
| column | type | notes |
|---|---|---|
| id | TEXT PK | ulid |
| kind | TEXT | rss, youtube_rss, takeout, opml, mcp, news_bias, youtube_oauth |
| name | TEXT | display name |
| config | TEXT JSON | url, channel_id, mcp server command/args, etc. |
| enabled | INTEGER | 0/1 |
| muted | INTEGER | rule: never show items from this source |
| affinity | REAL | learned from feedback, default 0 |
| last_pulled_at | TEXT | cursor |
| created_at | TEXT | |

### items
| column | type | notes |
|---|---|---|
| id | TEXT PK | ulid |
| url_hash | TEXT UNIQUE | sha256 of canonical URL |
| kind | TEXT | video, article, podcast, news |
| source_id | TEXT FK | |
| url | TEXT | |
| title | TEXT | |
| text | TEXT | description / excerpt, ≤ 4,000 chars |
| author | TEXT | |
| published_at | TEXT | |
| duration_s | INTEGER | nullable |
| language | TEXT | ISO 639-1, nullable |
| metadata | TEXT JSON | bias, factuality, channel_id, enclosure, etc. |
| seen_at | TEXT | when it first appeared in a served feed |
| created_at | TEXT | |

`items_fts` — FTS5 virtual table over `title, text` (content=items).
`items_vec` — sqlite-vec table `(item_id TEXT PK, embedding FLOAT[1024])`.

### signals
Consumption evidence, from imports or live connectors.
| column | type | notes |
|---|---|---|
| id | TEXT PK | |
| item_id | TEXT FK nullable | resolved when the item exists locally |
| url_hash | TEXT | to link later |
| kind | TEXT | watched, liked, subscribed, read, highlighted, listened |
| value | REAL | e.g. watch fraction, nullable |
| occurred_at | TEXT | |
| source_id | TEXT FK | |

### decisions
Cached Decision Contract answers.
| column | type | notes |
|---|---|---|
| item_id | TEXT FK | |
| question_set_version | TEXT | e.g. `v1` |
| backend_id | TEXT | `ollama:qwen3.5:4b`, `typesafe:jev-1.13.0`, `fake` |
| answers | TEXT JSON | `{name: {type, choice/score/p, probabilities, confidence, calibrated}}` |
| state_hash | TEXT | hash of the profile fragment used, for invalidation |
| created_at | TEXT | |
| PK | (item_id, question_set_version, backend_id) | |

### feedback
| column | type | notes |
|---|---|---|
| id | TEXT PK | |
| item_id | TEXT FK | |
| event | TEXT | like, dislike, less_of_this, opened, watched, dismissed, why_opened |
| payload | TEXT JSON | e.g. `{"target":"topic","value":"ai"}` for less_of_this |
| occurred_at | TEXT | |

### labels
Derived from feedback, consumed by calibration. One row per (item, field).
| column | type | notes |
|---|---|---|
| item_id | TEXT FK | |
| field | TEXT | fit, clickbait, avoid, … |
| label | REAL | 0/1 or ordinal |
| derived_from | TEXT | feedback.id |

### calibration
| column | type | notes |
|---|---|---|
| field | TEXT PK | |
| method | TEXT | temperature, isotonic |
| params | TEXT JSON | |
| n_labels | INTEGER | |
| ece | REAL | |
| fitted_at | TEXT | |

### profile
Single row (`id = 1`).
| column | type | notes |
|---|---|---|
| text | TEXT | natural-language profile, ≤ 600 tokens |
| topics | TEXT JSON | user taxonomy `[{"label","description"}]`, ≤ 40 |
| avoid | TEXT JSON | avoid-list strings |
| updated_at | TEXT | |

### rules
| column | type | notes |
|---|---|---|
| id | TEXT PK | |
| kind | TEXT | always, never, mute_source, min_duration, max_duration, language |
| match | TEXT JSON | `{"field":"title","regex":"…"}` or `{"topic":"…"}` |
| enabled | INTEGER | |

### settings
Key/value JSON: `weights` (per signal), `lambda_calibration`, `epsilon_exploration`, `pool_k`, `refresh_interval_min`, `decision_backend`, `question_set_version`.

### feed_snapshots
| column | type | notes |
|---|---|---|
| id | TEXT PK | |
| view | TEXT | default, videos, articles, podcasts, news |
| ranked | TEXT JSON | `[{item_id, score, breakdown}]` |
| created_at | TEXT | |

### user_vector
Single row: `embedding FLOAT[1024]`, `updated_at`, `n_items`.

## Breakdown JSON (contract with the UI)
```json
{
  "score": 0.73,
  "signals": [
    {"name": "fit", "raw": 3.2, "calibrated": 0.81, "weight": 0.35, "contribution": 0.28, "source": "decision:fit"},
    {"name": "clickbait", "raw": 0.12, "calibrated": 0.09, "weight": -0.2, "contribution": -0.02, "source": "decision:clickbait"},
    {"name": "recency", "raw": 0.9, "weight": 0.1, "contribution": 0.09, "source": "published_at"},
    {"name": "rule:always", "raw": 1, "weight": 1, "contribution": 0.0, "source": "rule:ulid…", "note": "pinned to top"}
  ],
  "rerank": {"calibration_penalty": -0.03, "exploration_slot": false},
  "topics": {"choice": "ai-engineering", "confidence": 0.71}
}
```
