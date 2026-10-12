"""UAT-16 / NFR-05: retry with exponential backoff."""
import pytest

from bc_client import BCApiError, with_retry


def fake_send(responses):
    it = iter(responses)
    return lambda: next(it)


def test_uat16_retries_on_429_then_succeeds():
    waits = []
    body = with_retry(fake_send([(429, {}), (503, {}), (201, {"id": "x"})]), sleep=waits.append)
    assert body == {"id": "x"}
    assert waits == [1, 2]


def test_validation_error_not_retried():
    waits = []
    with pytest.raises(BCApiError) as err:
        with_retry(fake_send([(400, {"error": {"message": "bad account"}})]), sleep=waits.append)
    assert err.value.status == 400 and waits == []


def test_gives_up_after_max_attempts():
    with pytest.raises(BCApiError):
        with_retry(fake_send([(429, {})] * 5), sleep=lambda s: None)
