"""The pure part of prober: the site list, one check, and one round of checks.

The HTTP calls go through functions handed in, so tests can replace them.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

log = logging.getLogger("prober")


@dataclass(frozen=True)
class Site:
    name: str  # what status calls it: "learn"
    url: str  # what gets requested: "https://learn.seandesmet.com/healthz"


@dataclass(frozen=True)
class Result:
    site: str
    url: str
    checked_at: datetime
    status_code: int | None  # None when there was no HTTP response at all
    response_ms: int | None
    error: str | None  # the exception's name and message when there was no response

    @property
    def up(self) -> bool:
        return self.error is None and self.status_code is not None and 200 <= self.status_code < 300

    def as_check(self) -> dict:
        """The body status's POST /checks expects."""
        return {
            "site": self.site,
            "status_code": self.status_code,
            "response_ms": self.response_ms,
            "error": self.error,
            "checked_at": self.checked_at.isoformat(),
        }


def parse_sites(text: str) -> list[Site]:
    """ "learn=https://…/healthz,budget=https://…" → [Site, …]. Whitespace and blanks ignored."""
    sites = []
    for item in text.replace("\n", ",").split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"site {item!r} must look like name=url")
        name, url = item.split("=", 1)
        name, url = name.strip(), url.strip()
        if not name or not url.startswith(("http://", "https://")):
            raise ValueError(f"site {item!r} must look like name=url with an http(s) url")
        sites.append(Site(name, url))
    return sites


def check_site(site: Site, client: httpx.Client) -> Result:
    """One GET of the site. Any status code is a result; no response at all is an error."""
    started = time.monotonic()
    now = datetime.now(UTC)
    try:
        response = client.get(site.url)
    except httpx.HTTPError as exc:
        return Result(site.name, site.url, now, None, None, f"{type(exc).__name__}: {exc}"[:200])
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return Result(site.name, site.url, now, response.status_code, elapsed_ms, None)


def run_once(
    sites: list[Site],
    check: Callable[[Site], Result],
    record: Callable[[Result, bool], None],
    send: Callable[[Result], None],
) -> list[Result]:
    """Check every site, record each result, try to send each to status.

    A site that fails doesn't stop the others. A send that fails is logged and the result is
    recorded as unsent; the loop carries on. What happens to unsent results is Step 3's question.
    """
    results = []
    for site in sites:
        try:
            result = check(site)
        except Exception as exc:  # noqa: BLE001 - one bad site must not stop the round
            log.exception("check of %s crashed", site.name)
            result = Result(
                site.name,
                site.url,
                datetime.now(UTC),
                None,
                None,
                f"{type(exc).__name__}: {exc}"[:200],
            )
        log.info(
            "check %s %s %s %sms%s",
            result.site,
            "up" if result.up else "DOWN",
            result.status_code,
            result.response_ms,
            f" ({result.error})" if result.error else "",
        )
        sent = True
        try:
            send(result)
        except Exception as exc:  # noqa: BLE001 - status being down is expected, not fatal
            sent = False
            log.warning("could not send %s to status: %s: %s", result.site, type(exc).__name__, exc)
        record(result, sent)
        results.append(result)
    return results
