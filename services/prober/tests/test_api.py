import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import Settings, create_app
from app.probe import Site


@pytest.fixture
def settings(tmp_path):
    return Settings(
        db_path=str(tmp_path / "prober.db"),
        sites=(Site("learn", "https://learn.example/healthz"),),
        status_url="http://status",
        interval_seconds=60,
        timeout_seconds=10,
    )


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings, run_loop=False)) as c:
        yield c


def test_healthz_readyz_and_state(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").status_code == 200
    state = client.get("/state").json()
    assert state["sites"] == [{"name": "learn", "url": "https://learn.example/healthz"}]
    assert state["last_run_at"] is None
    assert state["stored"] == {"total": 0, "unsent": 0}


def test_a_round_records_the_result_and_posts_it_to_status(client):
    prober = client.app.state.prober
    posted = []

    def status_handler(req):
        posted.append((req.url.path, req.read()))
        return httpx.Response(201)

    prober.sites_client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    prober.status_client = httpx.Client(transport=httpx.MockTransport(status_handler))
    prober.run_once()

    assert posted[0][0] == "/checks" and b'"site":"learn"' in posted[0][1]
    (row,) = client.get("/checks").json()
    assert (row["site"], row["status_code"], row["sent"]) == ("learn", 200, True)
    assert client.get("/state").json()["last_run_at"] is not None


def test_a_round_survives_status_being_down(client):
    prober = client.app.state.prober

    def down(req):
        raise httpx.ConnectError("connection refused")

    prober.sites_client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    prober.status_client = httpx.Client(transport=httpx.MockTransport(down))
    prober.run_once()
    (row,) = client.get("/checks").json()
    assert (row["status_code"], row["sent"]) == (200, False)
    assert client.get("/state").json()["stored"] == {"total": 1, "unsent": 1}
    assert client.get("/healthz").status_code == 200  # liveness unaffected


def test_settings_from_env_parses_the_site_list(monkeypatch, tmp_path):
    monkeypatch.setenv("SITES", "learn=https://a/healthz,www=https://b/")
    monkeypatch.setenv("STATUS_URL", "http://status/")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "p.db"))
    s = Settings.from_env()
    assert [x.name for x in s.sites] == ["learn", "www"]
    assert s.status_url == "http://status"
