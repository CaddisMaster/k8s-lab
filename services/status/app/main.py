"""The web side of status: a few FastAPI routes over the Store. (uvicorn runs app.asgi:app.)

Routes:
  GET  /healthz     liveness: the process answers (never looks at the database)
  GET  /readyz      readiness: the database can be read too
  POST /checks      the prober (or curl) reports one check result
  GET  /checks      recent raw results, for looking at
  GET  /api/sites   each site's state and uptime, as JSON
  GET  /            the same, as a page
"""

import html
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .db import Store
from .uptime import Check, state, uptime_percent

log = logging.getLogger("status")


@dataclass(frozen=True)
class Settings:
    db_path: str
    sites: tuple[str, ...]  # the sites the page always lists, in this order
    stale_after: timedelta  # no check this recent → "no data"
    window: timedelta  # uptime is worked out over this much history

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.environ.get("DB_PATH", "/data/status.db"),
            sites=tuple(s for s in os.environ.get("SITES", "learn,budget,www").split(",") if s),
            stale_after=timedelta(seconds=int(os.environ.get("STALE_AFTER_SECONDS", "180"))),
            window=timedelta(hours=int(os.environ.get("UPTIME_WINDOW_HOURS", "24"))),
        )


class CheckIn(BaseModel):
    """What a caller POSTs to /checks."""

    site: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9.-]*$")
    status_code: int | None = Field(default=None, ge=100, le=599)
    response_ms: int | None = Field(default=None, ge=0)
    error: str | None = Field(default=None, max_length=200)
    checked_at: datetime | None = None  # defaults to now; settable so tests can build history


class CheckOut(BaseModel):
    site: str
    checked_at: datetime
    status_code: int | None
    response_ms: int | None
    error: str | None
    up: bool


class SiteOut(BaseModel):
    site: str
    state: str  # "up", "down" or "no data"
    latest: CheckOut | None
    uptime_percent: float | None  # over the window; None with no checks in it


def _out(c: Check) -> CheckOut:
    return CheckOut(
        site=c.site,
        checked_at=c.checked_at,
        status_code=c.status_code,
        response_ms=c.response_ms,
        error=c.error,
        up=c.up,
    )


def create_app(settings: Settings) -> FastAPI:
    store = Store(settings.db_path)
    store.init()
    app = FastAPI(title="status", version="0.1.0")

    def summary(now: datetime) -> list[SiteOut]:
        names = list(settings.sites) + [s for s in store.sites() if s not in settings.sites]
        out = []
        for name in names:
            latest = store.latest(name)
            window = store.since(name, now - settings.window)
            out.append(
                SiteOut(
                    site=name,
                    state=state(latest, now, settings.stale_after),
                    latest=_out(latest) if latest else None,
                    uptime_percent=uptime_percent(window),
                )
            )
        return out

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(response: Response) -> dict[str, str]:
        try:
            store.ping()
        except Exception as exc:  # noqa: BLE001 - any failure means "not ready"
            log.warning("not ready: %s", exc)
            response.status_code = 503
            return {"status": "database unavailable"}
        return {"status": "ok"}

    @app.post("/checks", status_code=201)
    def post_check(body: CheckIn) -> CheckOut:
        when = body.checked_at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        check = Check(
            site=body.site,
            checked_at=when.astimezone(UTC),
            status_code=body.status_code,
            response_ms=body.response_ms,
            error=body.error,
        )
        store.insert(check)
        log.info(
            "check %s %s %s %sms",
            check.site,
            "up" if check.up else "DOWN",
            check.status_code,
            check.response_ms,
        )
        return _out(check)

    @app.get("/checks")
    def get_checks(
        site: str | None = None, limit: int = Query(default=50, ge=1, le=1000)
    ) -> list[CheckOut]:
        return [_out(c) for c in store.recent(site, limit)]

    @app.get("/api/sites")
    def api_sites() -> list[SiteOut]:
        return summary(datetime.now(UTC))

    @app.get("/", response_class=HTMLResponse)
    def page() -> str:
        now = datetime.now(UTC)
        return render(summary(now), now, settings)

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        raise HTTPException(status_code=404)

    return app


def render(sites: list[SiteOut], now: datetime, settings: Settings) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value))

    rows = []
    for s in sites:
        latest = s.latest
        if latest is None:
            seen, saw = "never", ""
        else:
            age = int((now - latest.checked_at).total_seconds())
            seen = f"{age}s ago" if age < 120 else f"{age // 60} min ago"
            if latest.error:
                saw = esc(latest.error)
            else:
                saw = f"{latest.status_code} in {latest.response_ms} ms"
        uptime = "–" if s.uptime_percent is None else f"{s.uptime_percent:.1f}%"
        css = s.state.replace(" ", "-")
        rows.append(
            f"<tr><td>{esc(s.site)}</td><td class='{css}'>{esc(s.state)}</td>"
            f"<td>{saw}</td><td>{esc(seen)}</td><td>{uptime}</td></tr>"
        )
    hours = int(settings.window.total_seconds() // 3600)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>status</title>
<meta http-equiv="refresh" content="30">
<style>
 body {{ font: 16px/1.4 system-ui, sans-serif; margin: 2rem auto; max-width: 48rem;
        padding: 0 1rem; }}
 table {{ border-collapse: collapse; width: 100%; }}
 th, td {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #ccc; }}
 .up {{ color: #1a7f37; font-weight: 600; }}
 .down {{ color: #c62828; font-weight: 600; }}
 .no-data {{ color: #777; }}
 footer {{ color: #777; font-size: .85rem; margin-top: 1rem; }}
</style></head><body>
<h1>status</h1>
<table><thead><tr><th>site</th><th>state</th><th>last check saw</th><th>when</th>
<th>uptime, {hours} h</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
<footer>{esc(now.strftime("%Y-%m-%d %H:%M:%S UTC"))}. "no data" after
{int(settings.stale_after.total_seconds())} s without a check. Refreshes every 30 s.</footer>
</body></html>"""
