from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import Settings, create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(
        db_path=str(tmp_path / "status.db"),
        sites=("learn", "budget", "www"),
        stale_after=timedelta(minutes=3),
        window=timedelta(hours=24),
    )


@pytest.fixture
def client(settings):
    return TestClient(create_app(settings))


def site(client, name):
    return next(s for s in client.get("/api/sites").json() if s["site"] == name)


def test_healthz_and_readyz(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").status_code == 200


def test_a_recorded_check_shows_as_up_with_what_it_saw(client):
    r = client.post("/checks", json={"site": "learn", "status_code": 200, "response_ms": 190})
    assert r.status_code == 201
    s = site(client, "learn")
    assert s["state"] == "up"
    assert (s["latest"]["status_code"], s["latest"]["response_ms"]) == (200, 190)
    page = client.get("/").text
    assert "learn" in page and "200 in 190 ms" in page


def test_a_site_with_no_recent_check_is_no_data_not_up(client):
    assert site(client, "budget")["state"] == "no data"
    old = (datetime.now(UTC) - timedelta(minutes=10)).isoformat()
    client.post("/checks", json={"site": "budget", "status_code": 200, "checked_at": old})
    assert site(client, "budget")["state"] == "no data"
    assert "no data" in client.get("/").text


def test_a_failed_check_shows_down_with_what_it_saw(client):
    client.post("/checks", json={"site": "www", "status_code": 503, "response_ms": 12})
    assert site(client, "www")["state"] == "down"
    assert "503 in 12 ms" in client.get("/").text
    client.post("/checks", json={"site": "www", "error": "timeout after 10 s"})
    assert site(client, "www")["state"] == "down"
    assert "timeout after 10 s" in client.get("/").text


def test_uptime_covers_the_last_24_hours_only(client):
    now = datetime.now(UTC)
    for i in range(10):
        code = 503 if i == 0 else 200
        when = (now - timedelta(hours=2 * i)).isoformat()
        client.post("/checks", json={"site": "learn", "status_code": code, "checked_at": when})
    # two days ago: must not count
    two_days_ago = (now - timedelta(days=2)).isoformat()
    client.post("/checks", json={"site": "learn", "status_code": 503, "checked_at": two_days_ago})
    assert site(client, "learn")["uptime_percent"] == 90.0
    assert "90.0%" in client.get("/").text


def test_data_survives_the_app_being_replaced(settings):
    TestClient(create_app(settings)).post("/checks", json={"site": "learn", "status_code": 200})
    again = TestClient(create_app(settings))  # a new pod, the same volume
    assert site(again, "learn")["latest"]["status_code"] == 200


def test_bad_input_is_rejected(client):
    assert client.post("/checks", json={"site": "", "status_code": 200}).status_code == 422
    assert client.post("/checks", json={"site": "learn", "status_code": 999}).status_code == 422
    assert client.post("/checks", json={"site": "learn", "response_ms": -1}).status_code == 422


def test_unknown_sites_are_listed_after_the_configured_ones(client):
    client.post("/checks", json={"site": "extra", "status_code": 200})
    names = [s["site"] for s in client.get("/api/sites").json()]
    assert names == ["learn", "budget", "www", "extra"]
