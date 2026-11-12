"""SQLite storage for check results.

One file, one table. A new connection per call keeps it simple and safe across uvicorn's
threads; SQLite's WAL mode lets reads and the single writer overlap.
"""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .uptime import Check

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
    id          INTEGER PRIMARY KEY,
    site        TEXT    NOT NULL,
    checked_at  TEXT    NOT NULL,   -- ISO 8601, UTC
    status_code INTEGER,
    response_ms INTEGER,
    error       TEXT,
    up          INTEGER NOT NULL    -- 0 or 1, worked out once at insert time
);
CREATE INDEX IF NOT EXISTS checks_site_time ON checks (site, checked_at);
"""


def _row_to_check(row: sqlite3.Row) -> Check:
    return Check(
        site=row["site"],
        checked_at=datetime.fromisoformat(row["checked_at"]),
        status_code=row["status_code"],
        response_ms=row["response_ms"],
        error=row["error"],
    )


class Store:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        """Create the file, the table and the index if they aren't there yet."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    def ping(self) -> None:
        """Raise if the database can't be read: the readiness probe's question."""
        with self._connect() as conn:
            conn.execute("SELECT count(*) FROM checks").fetchone()

    def insert(self, check: Check) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO checks (site, checked_at, status_code, response_ms, error, up)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    check.site,
                    check.checked_at.astimezone(UTC).isoformat(),
                    check.status_code,
                    check.response_ms,
                    check.error,
                    int(check.up),
                ),
            )
            return int(cur.lastrowid or 0)

    def latest(self, site: str) -> Check | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM checks WHERE site = ? ORDER BY checked_at DESC, id DESC LIMIT 1",
                (site,),
            ).fetchone()
        return _row_to_check(row) if row else None

    def since(self, site: str, since: datetime) -> list[Check]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM checks WHERE site = ? AND checked_at >= ? ORDER BY checked_at",
                (site, since.astimezone(UTC).isoformat()),
            ).fetchall()
        return [_row_to_check(r) for r in rows]

    def recent(self, site: str | None, limit: int) -> list[Check]:
        with self._connect() as conn:
            if site is None:
                rows = conn.execute(
                    "SELECT * FROM checks ORDER BY checked_at DESC, id DESC LIMIT ?", (limit,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM checks WHERE site = ? ORDER BY checked_at DESC, id DESC LIMIT ?",
                    (site, limit),
                ).fetchall()
        return [_row_to_check(r) for r in rows]

    def sites(self) -> list[str]:
        """Every site that has ever had a check, alphabetically."""
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT site FROM checks ORDER BY site").fetchall()
        return [r["site"] for r in rows]
