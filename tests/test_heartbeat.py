import pytest
from conftest import check

from betdex import BetDexAPIError, BetDexClient


def test_heartbeat_lifecycle(client: BetDexClient):
    """
    The heartbeat can be armed, read, updated and disarmed.
    """
    try:
        armed = check(client.send_heartbeat(60_000)).heartbeats[0]
        assert armed.active and armed.timeout_ms == 60_000

        assert check(client.get_heartbeat()).heartbeats[0].timeout_ms == 60_000

        updated = check(client.send_heartbeat(30_000)).heartbeats[0]
        assert updated.timeout_ms == 30_000
        assert updated.last_seen_at >= armed.last_seen_at
    finally:
        removed = check(client.delete_heartbeat()).heartbeats[0]

    assert removed.timeout_ms == 30_000
    with pytest.raises(BetDexAPIError) as error:
        client.get_heartbeat()
    assert error.value.status_code == 404
