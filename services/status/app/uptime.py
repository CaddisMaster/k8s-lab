"""The pure part of status: what a check means, and how state and uptime are worked out.

Nothing in here touches the database or the web framework, so it can be tested on its own.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

UP_RANGE = range(200, 300)


@dataclass(frozen=True)
class Check:
    """One check of one site, as the prober saw it."""

    site: str
    checked_at: datetime  # timezone-aware, UTC
    status_code: int | None  # None when there was no HTTP response at all
    response_ms: int | None
    error: str | None  # what went wrong when there was no response, e.g. "timeout"

    @property
    def up(self) -> bool:
        """A check is up when the site answered with a 2xx and nothing went wrong."""
        return self.error is None and self.status_code in UP_RANGE


def state(latest: Check | None, now: datetime, stale_after: timedelta) -> str:
    """Return "up", "down" or "no data".

    A site with no check at all, or whose latest check is older than `stale_after`, is
    "no data": a prober that has stopped must not leave the page green.
    """
    if latest is None or now - latest.checked_at > stale_after:
        return "no data"
    return "up" if latest.up else "down"


def uptime_percent(checks: list[Check]) -> float | None:
    """The share of checks that were up, as a percentage. None when there are no checks."""
    if not checks:
        return None
    return 100.0 * sum(1 for c in checks if c.up) / len(checks)
