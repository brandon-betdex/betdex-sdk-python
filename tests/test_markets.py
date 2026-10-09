import itertools

from conftest import NOW, WEEK_AGO, check

from betdex import BetDexClient
from betdex.markets import Market
from betdex.utils import paginate


def test_market_types(client: BetDexClient):
    """
    Market types can be listed and fetched by id.
    """
    types = check(client.get_market_types()).market_types
    assert types
    one = check(client.get_market_type(types[0].id)).market_types[0]
    assert one.outcomes_range.min <= one.outcomes_range.max


def test_markets(client: BetDexClient, open_market: Market):
    """
    Markets filter by status and can be fetched by id.
    """
    page = check(client.get_markets(statuses=["Open"], published=True, size=5))
    assert page.markets and all(m.status == "Open" for m in page.markets)
    one = check(client.get_market(open_market.id)).markets[0]
    assert one.id == open_market.id
    assert one.market_outcomes.ids == open_market.market_outcomes.ids


def test_markets_by_reference(client: BetDexClient):
    """
    An unknown external reference finds no markets.
    """
    assert check(client.get_markets_by_reference("FFT", "no-such-reference")).markets == []


def test_markets_historical(client: BetDexClient):
    """
    Settled markets can be read with keyset paging.
    """
    page = check(client.get_markets_historical("SettledDate", WEEK_AGO, NOW, limit=5))
    assert all(m.settled_at for m in page.documents.markets)


def test_market_prices(client: BetDexClient, open_market: Market):
    """
    All three price endpoints return a market's book.
    """
    check(client.get_market_prices(open_market.id, include_empty=True))
    book = check(client.get_market_prices_v2(open_market.id)).prices[0]
    assert book.market_id == open_market.id
    books = check(client.get_markets_prices([open_market.id], direct_only=True)).prices
    assert [b.market_id for b in books] == [open_market.id]


def test_market_price_ladder(client: BetDexClient):
    """
    The price ladder spans 1.01 to 1000.
    """
    prices = check(client.get_market_price_ladder()).market_price_ladders[0].prices
    assert prices[0] == 1.01 and prices[-1] == 1000.0


def test_market_positions(client: BetDexClient, open_market: Market, wallet_id: str):
    """
    A market's positions can be read for a wallet.
    """
    check(client.get_market_positions(open_market.id, wallet_ids=[wallet_id]))


def test_settled_market_is_not_in_play(client: BetDexClient, open_market: Market):
    """
    A settled market that still says ``InPlay`` is not in play; nor is a pre-play one.
    """
    settled = client.get_markets(statuses=["Settled"], size=100).markets
    stale = [m for m in settled if m.in_play_status == "InPlay"]
    assert stale and not any(m.is_in_play for m in stale)
    assert not open_market.is_in_play


def test_available_to_back_and_lay(client: BetDexClient):
    """
    A book lists backable prices (resting Against) highest first and layable
    prices (resting For) lowest first.
    """
    books = []
    for page in itertools.islice(paginate(client.get_markets, statuses=["Open"], size=100), 20):
        ids = [m.id for m in page.markets]
        books = [b for b in client.get_markets_prices(ids).prices if b.prices] if ids else []
        if books:
            break
    assert books, "no open market with prices"
    for book in books:
        for outcome_id in {p.outcome_id for p in book.prices}:
            back, lay = book.available_to_back(outcome_id), book.available_to_lay(outcome_id)
            assert all(p.side == "Against" and p.outcome_id == outcome_id for p in back)
            assert all(p.side == "For" and p.outcome_id == outcome_id for p in lay)
            assert [p.price for p in back] == sorted((p.price for p in back), reverse=True)
            assert [p.price for p in lay] == sorted(p.price for p in lay)
