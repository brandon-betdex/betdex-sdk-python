import os
from datetime import datetime, timezone

import pytest
from conftest import CREDENTIALS, check

from betdex import BetDexAPIError, BetDexClient


def test_create_session_authenticates_later_calls(client: BetDexClient):
    """
    Logging in stores the tokens, turning a 401 into a successful call.
    """
    fresh = BetDexClient(*(os.environ[name] for name in CREDENTIALS), environment="sandbox")
    with pytest.raises(BetDexAPIError) as error:
        fresh.get_wallet()
    assert error.value.status_code == 401

    session = check(fresh.create_session()).sessions[0]

    assert fresh.conn.access_token == session.access_token
    assert session.access_expires_at < session.refresh_expires_at
    assert fresh.get_wallet().wallets


def test_refresh_session_replaces_the_tokens(client: BetDexClient):
    """
    Refreshing swaps in new tokens that still authenticate.
    """
    fresh = BetDexClient(*(os.environ[name] for name in CREDENTIALS), environment="sandbox")
    first = fresh.create_session().sessions[0]

    refreshed = check(fresh.refresh_session()).sessions[0]

    assert refreshed.access_token != first.access_token
    assert fresh.conn.refresh_token == refreshed.refresh_token
    assert fresh.get_wallet().wallets


def test_get_commission_rates(client: BetDexClient):
    """
    The app's commission rates can be read.
    """
    check(client.get_commission_rates())


def test_responses_and_errors_are_timed(client: BetDexClient):
    """
    Responses and API errors carry when the request was sent, when the answer
    arrived and the round trip.
    """
    before = datetime.now(timezone.utc)
    result = client.get_commission_rates()
    assert before <= result.sent_at <= result.received_at <= datetime.now(timezone.utc)
    assert 0 < result.latency_ms < 30_000

    with pytest.raises(BetDexAPIError) as error:
        client.get_trade("999999999999")
    failed = error.value
    assert result.received_at <= failed.sent_at <= failed.received_at
    assert 0 < failed.latency_ms < 30_000
