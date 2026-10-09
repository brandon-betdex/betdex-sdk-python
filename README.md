# betdex

A Python client for the [BetDEX Exchange API](https://developers.betdex.com) (REST and Stream).

- One typed method per endpoint on a single `BetDexClient`
- Responses are dataclasses; each keeps its raw JSON (`.raw`) plus `sent_at`, `received_at` and `latency_ms`
- A blocking stream with pluggable listeners.

```sh
pip install betdex
```

## Quick Start

```python
from betdex import BetDexClient

client = BetDexClient(app_id, api_key, wallet_id, environment="sandbox")  # or "prod"
client.create_session()

markets = client.get_markets(statuses=["Open"], size=10).markets
live = [m for m in markets if m.is_in_play]

book = client.get_market_prices_v2(markets[0].id).prices[0]
best_back = book.available_to_back(outcome_id)[:1]
best_lay = book.available_to_lay(outcome_id)[:1]
```

## Orders

```python
from betdex.utils import batch, new_reference

order = client.create_order(market_id, outcome_id, "For", price=2.5, stake=10,
                            keep_when_in_play=False, reference=new_reference("bot_")).orders[0]
print(order.status, order.stake_matched, order.liability)

for result in batch(client.create_orders, requests):    # 50 per call
    ...

client.cancel_orders(wallet_ids=[wallet_id])
```

## Paging

- Many endpoints are paginated. A `paginate` utility is supplied:

```python
from betdex.utils import paginate

for page in paginate(client.get_markets, event_ids=["123"]):
    ...
```

## Errors

- All errors derive from `BetDexError`:

```python
from betdex import BetDexAPIError, BetDexTransportError

try:
    client.get_order("123")
except BetDexAPIError as exc:          # error status: status_code, title, details, response
    print(exc.status_code, exc.title, exc.latency_ms)
except BetDexTransportError as exc:    # no response
    print(exc, exc.latency_ms)
```



## Streaming

```python
import threading
from betdex.streaming import MarketBook, OrderUpdate, StreamListener

listener = StreamListener()
stream = client.create_stream(listener)
stream.subscribe_to_orders()
stream.subscribe_to_market_prices(["123"])         # or no argument for every market
threading.Thread(target=stream.start, daemon=True).start()

while True:
    update = listener.output_queue.get()
    if isinstance(update, MarketBook):
        best_back = update.available_to_back(outcome_id)[:1]
    elif isinstance(update, OrderUpdate):
        filled = update.stake_matched
```

- `start()` blocks; `stop()` ends it from any thread
- On a dropped connection `start()` raises `BetDexSocketError`; call it again to reconnect and resubscribe
- Updates missed while disconnected aren't replayed; catch up on orders with `get_orders`
- For raw frames, subclass `BaseListener` and override `on_data(raw)`

## Execution

```python
from betdex.execution import add_ticks, round_down_to_nearest_price

round_down_to_nearest_price(5.55)    # 5.5
add_ticks(1.99, 2)                   # 2.02
```
