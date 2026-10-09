import pytest
from conftest import NOW, WEEK_AGO, check

from betdex import BetDexClient, BetDexInvalidRequestError
from betdex.markets import Market


def test_get_wallet_defaults_to_the_client_wallet(client: BetDexClient, wallet_id: str):
    """
    get_wallet falls back to the client's wallet and requires one.
    """
    wallet = check(client.get_wallet()).wallets[0]
    assert wallet.id == wallet_id
    assert check(client.get_wallet(wallet_id)).wallets[0].id == wallet.id
    with pytest.raises(BetDexInvalidRequestError):
        BetDexClient().get_wallet()


def test_get_wallets(client: BetDexClient, wallet_id: str):
    """
    Wallets filter by id.
    """
    page = check(client.get_wallets(wallet_ids=[wallet_id]))
    assert [w.id for w in page.wallets] == [wallet_id]


def test_wallet_transactions(client: BetDexClient, wallet_id: str):
    """
    The wallet's ledger can be read, newest first.
    """
    page = check(client.get_wallet_transactions(size=5, sort=["createdAt,desc"]))
    assert page.transactions and page.transactions[0].wallet_id == wallet_id


def test_wallet_positions(client: BetDexClient, open_market: Market):
    """
    Positions can be read for given markets and across the wallet.
    """
    check(client.get_wallet_positions([open_market.id]))
    check(client.get_all_wallet_positions(filter="Active", size=5))


def test_wallet_metrics(client: BetDexClient):
    """
    The wallet's order metrics can be read for a time window.
    """
    currency = client.get_wallet().wallets[0].balances[0].currency_id
    metrics = check(client.get_wallet_metrics(currency, WEEK_AGO, NOW)).wallet_metrics
    assert metrics.cancelled.count >= 0
