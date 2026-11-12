from datetime import UTC, datetime

import httpx
import pytest

from app.probe import Result, Site, check_site, parse_sites, run_once

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)


def test_parse_sites_reads_name_equals_url_pairs():
    text = "learn=https://learn.example/healthz, www=https://www.example/\n"
    assert parse_sites(text) == [
        Site("learn", "https://learn.example/healthz"),
        Site("www", "https://www.example/"),
    ]
    assert parse_sites("") == []


@pytest.mark.parametrize("bad", ["learn", "=https://x", "learn=ftp://x", "learn=x"])
def test_parse_sites_rejects_malformed_entries(bad):
    with pytest.raises(ValueError):
        parse_sites(bad)


def client_answering(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_check_site_records_the_status_code_and_time():
    client = client_answering(lambda req: httpx.Response(200, text="ok"))
    r = check_site(Site("learn", "https://learn.example/healthz"), client)
    assert (r.status_code, r.error, r.up) == (200, None, True)
    assert r.response_ms is not None and r.response_ms >= 0


def test_check_site_treats_a_non_2xx_as_down_but_still_a_result():
    client = client_answering(lambda req: httpx.Response(503))
    r = check_site(Site("www", "https://www.example/"), client)
    assert (r.status_code, r.error, r.up) == (503, None, False)


def test_check_site_turns_no_response_into_an_error():
    def refuse(req):
        raise httpx.ConnectError("connection refused")

    r = check_site(Site("www", "https://www.example/"), client_answering(refuse))
    assert r.status_code is None and r.response_ms is None
    assert r.error == "ConnectError: connection refused"
    assert not r.up


def result(site: str, code: int | None = 200, error: str | None = None) -> Result:
    return Result(site, f"https://{site}.example/", NOW, code, 10, error)


def test_run_once_checks_every_site_even_when_one_fails():
    def check(site):
        if site.name == "budget":
            raise RuntimeError("boom")
        return result(site.name)

    recorded, sent = [], []
    sites = [Site(n, f"https://{n}.example/") for n in ("learn", "budget", "www")]
    results = run_once(sites, check, lambda r, ok: recorded.append((r.site, ok)), sent.append)
    assert [r.site for r in results] == ["learn", "budget", "www"]
    assert results[1].error == "RuntimeError: boom"
    assert recorded == [("learn", True), ("budget", True), ("www", True)]
    assert len(sent) == 3


def test_run_once_keeps_the_result_and_carries_on_when_status_is_unreachable():
    def send(r):
        raise httpx.ConnectError("status is down")

    recorded = []
    sites = [Site("learn", "https://learn.example/"), Site("www", "https://www.example/")]
    results = run_once(
        sites, lambda s: result(s.name), lambda r, ok: recorded.append((r.site, ok)), send
    )
    assert len(results) == 2
    assert recorded == [("learn", False), ("www", False)]  # kept, marked unsent


def test_as_check_is_what_status_accepts():
    body = result("learn", None, "ConnectTimeout: x").as_check()
    assert body == {
        "site": "learn",
        "status_code": None,
        "response_ms": 10,
        "error": "ConnectTimeout: x",
        "checked_at": "2026-11-11T12:00:00+00:00",
    }
