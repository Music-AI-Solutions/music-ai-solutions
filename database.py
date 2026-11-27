"""SQLite registry of fingerprinted tracks."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

from fingerprint import similarity
from models import TrackRecord

DB_PATH = os.environ.get("MAS_DB", "registry.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    fingerprint_id TEXT NOT NULL,
    duration_s REAL NOT NULL,
    registered_at TEXT NOT NULL,
    hashes TEXT NOT NULL
)
"""


def _connect(path=None):
    conn = sqlite3.connect(path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def _record(row) -> TrackRecord:
    return TrackRecord(**{k: row[k] for k in TrackRecord.__dataclass_fields__})


def register_track(title, artist, fp, path=None) -> TrackRecord:
    rec = TrackRecord(
        id=str(uuid.uuid4()),
        title=title,
        artist=artist,
        sha256=fp["sha256"],
        fingerprint_id=fp["fingerprint_id"],
        duration_s=fp["duration_s"],
        registered_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    with _connect(path) as conn:
        conn.execute(
            "INSERT INTO tracks VALUES (?,?,?,?,?,?,?,?)",
            (*rec.to_dict().values(), json.dumps(fp["hashes"])),
        )
    return rec


def get_track(track_id, path=None):
    with _connect(path) as conn:
        row = conn.execute("SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()
    return _record(row) if row else None


def find_similar(fp, threshold=0.3, path=None):
    """Registered tracks whose fingerprint overlaps this one, best match first."""
    with _connect(path) as conn:
        rows = conn.execute("SELECT * FROM tracks").fetchall()
    matches = []
    for row in rows:
        score = similarity(fp["hashes"], json.loads(row["hashes"]))
        if score >= threshold:
            matches.append({"score": round(score, 3), "track": _record(row).to_dict()})
    return sorted(matches, key=lambda m: m["score"], reverse=True)
