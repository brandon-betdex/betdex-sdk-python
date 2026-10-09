import pytest

from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

from conftest import NOW, WEEK_AGO, check
from betdex import BetDexAPIError, BetDexClient, BetDexInvalidRequestError
from betdex.markets import Market
from betdex.orders import CreateOrderRequest, Order, OrderFailure, OrderID
from betdex.utils import MAX_BATCH_SIZE, batch, new_reference
from betdex.wallets import WalletBalance


PRICE, STAKE = 1000.0, 1.0
PREFIX = "sdk-test_"
MIN_AVAILABLE = 100.0
MAX_FAUCET_DRAWS = 5


def request(market: Market, wallet_id: str, reference: str) -> CreateOrderRequest:
    """
    Build a request for a test order on ``market`` that will rest unmatched.
    """
    return CreateOrderRequest(
        wallet_id=wallet_id, market_id=market.id, side="For",
        outcome_id=market.market_outcomes.ids[0], price=PRICE, stake=STAKE,
        keep_when_in_play=False, reference=reference)


def available(balances: list[WalletBalance], currency_id: str) -> float:
    """
    The available balance in ``currency_id``, or 0 if the wallet holds none.
    """
    return next((b.balance_available for b in balances if b.currency_id == currency_id), 0.0)


@pytest.fixture(scope="module", autouse=True)
def funded_wallet(client: BetDexClient, wallet_id: str, open_market: Market) -> Iterator[None]:
    """
    Top the wallet up from the faucet before the order tests; cancel every order
    left resting in it afterwards.
    """
    currency = open_market.currency_id
    balance = available(client.get_wallet().wallets[0].balances, currency)
    for _ in range(MAX_FAUCET_DRAWS):
        if balance >= MIN_AVAILABLE:
            break
        balance = available(check(client.credit_wallet(currency)).wallet.balances, currency)
    assert balance >= MIN_AVAILABLE, f"wallet has {balance} available after the faucet"

    yield

    client.cancel_orders(wallet_ids=[wallet_id])
    resting = client.get_orders(wallet_ids=[wallet_id], statuses=["Unmatched", "PartiallyMatched"])
    assert resting.orders == [], "orders still resting after the wallet-wide cancel"


@pytest.fixture
def resting_order(client: BetDexClient, open_market: Market) -> Iterator[Order]:
    """
    One unmatched order on ``open_market``, cancelled afterwards.
    """
    reference = new_reference(PREFIX)
    order = client.create_order(
        open_market.id, open_market.market_outcomes.ids[0], "For", PRICE, STAKE,
        keep_when_in_play=False, reference=reference).orders[0]
    try:
        yield order
    finally:
        client.cancel_orders(order_ids=[order.id])


def test_create_order(client: BetDexClient, open_market: Market):
    """
    A placed order rests unmatched with the given reference, price and stake.
    """
    reference = new_reference(PREFIX)
    result = check(client.create_order(
        open_market.id, open_market.market_outcomes.ids[0], "For", PRICE, STAKE,
        keep_when_in_play=False, reference=reference))
    order = result.orders[0]
    try:
        assert (order.status, order.reference, order.price, order.stake_unmatched) == (
            "Unmatched", reference, PRICE, STAKE)
        assert order.market.ids == [open_market.id]
    finally:
        client.cancel_orders(order_ids=[order.id])


def test_liability_and_matched_stake(client: BetDexClient, open_market: Market):
    """
    A resting order has nothing matched; its liability is the stake for ``For``
    and ``stake * (price - 1)`` for ``Against``.
    """
    outcome_id = open_market.market_outcomes.ids[0]
    back = client.create_order(open_market.id, outcome_id, "For", PRICE, STAKE,
                               keep_when_in_play=False, reference=new_reference(PREFIX))
    lay = client.create_order(open_market.id, outcome_id, "Against", 1.01, STAKE,
                              keep_when_in_play=False, reference=new_reference(PREFIX))
    orders = [back.orders[0], lay.orders[0]]
    try:
        assert [o.stake_matched for o in orders] == [0, 0]
        assert orders[0].liability == STAKE
        assert orders[1].liability == pytest.approx(STAKE * 0.01)
    finally:
        client.cancel_orders(order_ids=[o.id for o in orders])


def test_read_an_order_back(
    client: BetDexClient,
    open_market: Market,
    resting_order: Order,
    wallet_id: str,
    app_id: str):
    """
    A resting order is found by id, reference, filters and market, with no trades.
    """
    reference = resting_order.reference
    assert reference is not None
    assert check(client.get_order(resting_order.id)).orders[0].id == resting_order.id
    by_reference = check(client.get_order_by_reference(reference)).orders[0]
    assert by_reference.id == resting_order.id

    page = check(client.get_orders(
        ids=[resting_order.id], wallet_ids=[wallet_id], statuses=["Unmatched"]))
    assert [o.id for o in page.orders] == [resting_order.id]
    page = check(client.get_orders(
        references=[reference], app_ids=[app_id]))
    assert [o.id for o in page.orders] == [resting_order.id]

    on_market = check(client.get_market_orders(open_market.id, wallet_ids=[wallet_id]))
    assert resting_order.id in {o.id for o in on_market.orders}
    assert check(client.get_order_trades(resting_order.id)).trades == []


def test_create_orders_reports_each_order(
    client: BetDexClient,
    open_market: Market,
    wallet_id: str):
    """
    A batch places its valid orders and reports failures for the rest.
    """
    good = request(open_market, wallet_id, new_reference(PREFIX))
    bad = CreateOrderRequest(
        wallet_id=wallet_id, market_id="999999999", side="For",
        outcome_id=open_market.market_outcomes.ids[0], price=PRICE, stake=STAKE,
        keep_when_in_play=False)
    result = check(client.create_orders([good, bad]))
    placed = [o for o in result.orders if isinstance(o, Order)]
    try:
        assert [o.reference for o in placed] == [good.reference]
        failure = next(o for o in result.orders if isinstance(o, OrderFailure))
        assert failure.error_code == "MARKET_NOT_FOUND"
    finally:
        client.cancel_orders(order_ids=[o.id for o in placed])


def test_batch_places_more_than_one_batch(
    client: BetDexClient,
    open_market: Market,
    wallet_id: str):
    """
    ``batch`` splits more orders than one call takes, and places them all.
    """
    requests = [request(open_market, wallet_id, new_reference(PREFIX))
                for _ in range(MAX_BATCH_SIZE + 1)]
    results = list(batch(client.create_orders, requests))
    placed = [o for r in results for o in r.orders if isinstance(o, Order)]
    try:
        assert [len(r.orders) for r in results] == [MAX_BATCH_SIZE, 1]
        assert [o.reference for o in placed] == [r.reference for r in requests]
    finally:
        client.cancel_orders(order_ids=[o.id for o in placed])
    with pytest.raises(BetDexInvalidRequestError):
        next(batch(client.create_orders, requests, size=MAX_BATCH_SIZE + 1))


def test_cancel_orders(client: BetDexClient, open_market: Market, wallet_id: str):
    """
    Cancelled orders report back, change status and appear in the cancelled list.
    """
    result = client.create_orders(
        [request(open_market, wallet_id, new_reference(PREFIX)) for _ in range(2)])
    ids = sorted(o.id for o in result.orders if isinstance(o, Order))
    assert len(ids) == 2

    cancelled = check(client.cancel_orders(order_ids=ids))

    assert sorted(cancelled.ids) == ids
    assert {client.get_order(i).orders[0].status for i in ids} == {"Cancelled"}
    # Only this test's window, so earlier runs' cancels can't fill the page.
    window_start = result.sent_at - timedelta(minutes=1)
    window_end = datetime.now(timezone.utc) + timedelta(minutes=1)
    recent = check(client.get_orders_cancelled(window_start, window_end, limit=500))
    assert set(ids) <= {o.id for o in recent.documents.orders}


def test_settled_and_historical_orders(client: BetDexClient, wallet_id: str):
    """
    Settled and historical orders can be read.
    """
    check(client.get_orders_settled(WEEK_AGO, NOW, wallet_id=wallet_id, size=5))
    check(client.get_orders_historical("SettledDate", WEEK_AGO, NOW, limit=5))


def test_trades(client: BetDexClient, wallet_id: str):
    """
    Trades can be listed, fetched by id and read historically; an unknown id is a 404.
    """
    page = check(client.get_trades(wallet_ids=[wallet_id], size=5))
    for trade in page.trades[:1]:
        assert check(client.get_trade(trade.id)).trades[0].id == trade.id
    check(client.get_trades_historical("SettledDate", WEEK_AGO, NOW, limit=5))
    with pytest.raises(BetDexAPIError) as error:
        client.get_trade("999999999999")
    assert error.value.status_code == 404


def test_create_order_request(client: BetDexClient, open_market: Market):
    """
    An order request creates an order findable by its reference.
    """
    reference = new_reference(PREFIX)
    result = check(client.create_order_request(
        open_market.id, open_market.market_outcomes.ids[0], "For", PRICE, STAKE,
        keep_when_in_play=False, reference=reference))
    try:
        order = client.get_order_by_reference(reference).orders[0]
        assert result.ids == [order.id]
    finally:
        client.cancel_orders(order_ids=result.ids)


def test_create_order_requests(client: BetDexClient, open_market: Market, wallet_id: str):
    """
    A batch of order requests creates orders findable by reference.
    """
    reference = new_reference(PREFIX)
    result = check(client.create_order_requests([request(open_market, wallet_id, reference)]))
    accepted = [r.id for r in result.ids if isinstance(r, OrderID)]
    try:
        assert accepted == [client.get_order_by_reference(reference).orders[0].id]
    finally:
        client.cancel_orders(order_ids=accepted)
