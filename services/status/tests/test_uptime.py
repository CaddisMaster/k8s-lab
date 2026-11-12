from datetime import UTC, datetime, timedelta

from app.uptime import Check, state, uptime_percent

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
STALE = timedelta(minutes=3)


def check(minutes_ago: int, status_code: int | None = 200, error: str | None = None) -> Check:
    return Check("learn", NOW - timedelta(minutes=minutes_ago), status_code, 190, error)


def test_2xx_is_up_and_anything_else_is_down():
    assert check(0, 200).up
    assert check(0, 204).up
    assert not check(0, 503).up
    assert not check(0, 404).up
    assert not check(0, None, "timeout").up
    assert not check(0, 200, "tls error").up  # an error wins over a code


def test_state_follows_the_latest_check_while_it_is_fresh():
    assert state(check(1, 200), NOW, STALE) == "up"
    assert state(check(1, 503), NOW, STALE) == "down"


def test_state_is_no_data_without_a_recent_check():
    assert state(None, NOW, STALE) == "no data"
    assert state(check(4, 200), NOW, STALE) == "no data"  # fresh enough? no: older than 3 min


def test_uptime_is_the_share_of_checks_that_were_up():
    checks = [check(i, 200) for i in range(9)] + [check(9, 503)]
    assert uptime_percent(checks) == 90.0
    assert uptime_percent([]) is None
