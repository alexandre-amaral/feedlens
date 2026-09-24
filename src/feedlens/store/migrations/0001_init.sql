-- feedlens schema v1 — see docs/DATA_MODEL.md
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  config TEXT NOT NULL DEFAULT '{}',
  enabled INTEGER NOT NULL DEFAULT 1,
  muted INTEGER NOT NULL DEFAULT 0,
  affinity REAL NOT NULL DEFAULT 0,
  last_pulled_at TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,
  url_hash TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('video','article','podcast','news')),
  source_id TEXT REFERENCES sources(id) ON DELETE SET NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  text TEXT NOT NULL DEFAULT '',
  author TEXT,
  published_at TEXT,
  duration_s INTEGER,
  language TEXT,
  metadata TEXT NOT NULL DEFAULT '{}',
  seen_at TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS items_published ON items(published_at);
CREATE INDEX IF NOT EXISTS items_source ON items(source_id);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(title, text, content='items', content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
  INSERT INTO items_fts(rowid, title, text) VALUES (new.rowid, new.title, new.text);
END;
CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
  INSERT INTO items_fts(items_fts, rowid, title, text) VALUES ('delete', old.rowid, old.title, old.text);
END;
CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
  INSERT INTO items_fts(items_fts, rowid, title, text) VALUES ('delete', old.rowid, old.title, old.text);
  INSERT INTO items_fts(rowid, title, text) VALUES (new.rowid, new.title, new.text);
END;

-- requires sqlite-vec loaded; dimension must match FEEDLENS_EMBED_DIM
CREATE VIRTUAL TABLE IF NOT EXISTS items_vec USING vec0(item_id TEXT PRIMARY KEY, embedding FLOAT[1024]);

CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY,
  item_id TEXT REFERENCES items(id) ON DELETE SET NULL,
  url_hash TEXT NOT NULL,
  kind TEXT NOT NULL,
  value REAL,
  occurred_at TEXT NOT NULL,
  source_id TEXT REFERENCES sources(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS signals_url ON signals(url_hash);
CREATE INDEX IF NOT EXISTS signals_time ON signals(occurred_at);

CREATE TABLE IF NOT EXISTS decisions (
  item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  question_set_version TEXT NOT NULL,
  backend_id TEXT NOT NULL,
  answers TEXT NOT NULL,
  state_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (item_id, question_set_version, backend_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  payload TEXT NOT NULL DEFAULT '{}',
  occurred_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS labels (
  item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  field TEXT NOT NULL,
  label REAL NOT NULL,
  derived_from TEXT NOT NULL,
  PRIMARY KEY (item_id, field, derived_from)
);

CREATE TABLE IF NOT EXISTS calibration (
  field TEXT PRIMARY KEY,
  method TEXT NOT NULL,
  params TEXT NOT NULL,
  n_labels INTEGER NOT NULL,
  ece REAL,
  fitted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  text TEXT NOT NULL DEFAULT '',
  topics TEXT NOT NULL DEFAULT '[]',
  avoid TEXT NOT NULL DEFAULT '[]',
  depth_pref INTEGER NOT NULL DEFAULT 2,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rules (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  match TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  learned INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feed_snapshots (
  id TEXT PRIMARY KEY,
  view TEXT NOT NULL,
  ranked TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS snapshots_view ON feed_snapshots(view, created_at);

CREATE TABLE IF NOT EXISTS user_vector (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  embedding BLOB NOT NULL,
  n_items INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);
