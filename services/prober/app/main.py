"""The web side of prober, and the loop that does the checking. (uvicorn runs app.asgi:app.)

Routes:
  GET /healthz   liveness: the process answers (looks at nothing else: not status, not the sites)
  GET /readyz    readiness: the database can be read too
  GET /checks    prober's own record of recent results, with whether status received each
  GET /state     the site list, the interval, and when the loop last ran
"""

import logging
import os
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI, Query, Response

from .db import Store
from .probe import Result, Site, check_site, parse_sites, run_once

log = logging.getLogger("prober")


@dataclass(frozen=True)
class Settings:
    db_path: str
    sites: tuple[Site, ...]
    status_url: str  # where results go: http://status, the Service name
    interval_seconds: float
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.environ.get("DB_PATH", "/data/prober.db"),
            sites=tuple(parse_sites(os.environ.get("SITES", ""))),
            status_url=os.environ.get("STATUS_URL", "http://status").rstrip("/"),
            interval_seconds=float(os.environ.get("INTERVAL_SECONDS", "60")),
            timeout_seconds=float(os.environ.get("TIMEOUT_SECONDS", "10")),
        )


class Prober:
    """Owns the HTTP clients and runs rounds of checks, on demand or on a timer."""

    def __init__(self, settings: Settings, store: Store) -> None:
        self.settings = settings
        self.store = store
        self.sites_client = httpx.Client(
            timeout=settings.timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "k8s-lab prober/0.1.0"},
        )
        self.status_client = httpx.Client(timeout=5)
        self.last_run_at: datetime | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def send(self, result: Result) -> None:
        self.status_client.post(
            f"{self.settings.status_url}/checks", json=result.as_check()
        ).raise_for_status()

    def run_once(self) -> list[Result]:
        results = run_once(
            list(self.settings.sites),
            check=lambda site: check_site(site, self.sites_client),
            record=self.store.insert,
            send=self.send,
        )
        self.last_run_at = datetime.now(UTC)
        return results

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:  # noqa: BLE001 - the loop must outlive any one round
                log.exception("round failed")
            self._stop.wait(self.settings.interval_seconds)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="prober-loop", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        self.sites_client.close()
        self.status_client.close()


def create_app(settings: Settings, run_loop: bool = True) -> FastAPI:
    store = Store(settings.db_path)
    store.init()
    prober = Prober(settings, store)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # Runs once at startup (before the yield) and once at shutdown (after it).
        log.info(
            "checking %d site(s) every %ss, sending to %s",
            len(settings.sites),
            settings.interval_seconds,
            settings.status_url,
        )
        for site in settings.sites:
            log.info("site %s = %s", site.name, site.url)
        if run_loop:
            prober.start()
        yield
        prober.stop()

    app = FastAPI(title="prober", version="0.1.0", lifespan=lifespan)
    app.state.prober = prober

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(response: Response) -> dict[str, str]:
        try:
            store.ping()
        except Exception as exc:  # noqa: BLE001
            log.warning("not ready: %s", exc)
            response.status_code = 503
            return {"status": "database unavailable"}
        return {"status": "ok"}

    @app.get("/checks")
    def checks(
        site: str | None = None, limit: int = Query(default=50, ge=1, le=1000)
    ) -> list[dict]:
        return store.recent(site, limit)

    @app.get("/state")
    def state() -> dict:
        return {
            "sites": [{"name": s.name, "url": s.url} for s in settings.sites],
            "status_url": settings.status_url,
            "interval_seconds": settings.interval_seconds,
            "timeout_seconds": settings.timeout_seconds,
            "last_run_at": prober.last_run_at,
            "stored": store.counts(),
        }

    return app
