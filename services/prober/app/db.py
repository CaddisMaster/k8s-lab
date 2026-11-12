"""SQLite storage for prober's own record of every check, and whether status received it."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .probe import Result

SCHEMA = """
CREATE TABLE IF NOT EXISTS results (
    id          INTEGER PRIMARY KEY,
    site        TEXT    NOT NULL,
    url         TEXT    NOT NULL,
    checked_at  TEXT    NOT NULL,   -- ISO 8601, UTC
    status_code INTEGER,
    response_ms INTEGER,
    error       TEXT,
    sent        INTEGER NOT NULL    -- 1 if status accepted it, 0 if the send failed
);
CREATE INDEX IF NOT EXISTS results_time ON results (checked_at);
"""


class Store:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    def ping(self) -> None:
        with self._connect() as conn:
            conn.execute("SELECT count(*) FROM results").fetchone()

    def insert(self, result: Result, sent: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO results (site, url, checked_at, status_code, response_ms, error, sent)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    result.site,
                    result.url,
                    result.checked_at.astimezone(UTC).isoformat(),
                    result.status_code,
                    result.response_ms,
                    result.error,
                    int(sent),
                ),
            )

    def recent(self, site: str | None, limit: int) -> list[dict]:
        with self._connect() as conn:
            if site is None:
                rows = conn.execute(
                    "SELECT * FROM results ORDER BY checked_at DESC, id DESC LIMIT ?", (limit,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM results WHERE site = ? ORDER BY checked_at DESC, id DESC"
                    " LIMIT ?",
                    (site, limit),
                ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["checked_at"] = datetime.fromisoformat(d["checked_at"])
            d["sent"] = bool(d["sent"])
            out.append(d)
        return out

    def counts(self) -> dict[str, int]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT count(*) AS total, coalesce(sum(1 - sent), 0) AS unsent FROM results"
            ).fetchone()
        return {"total": row["total"], "unsent": row["unsent"]}
