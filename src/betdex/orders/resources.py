from dataclasses import dataclass, field
from datetime import datetime

from betdex.events.resources import (
    CategorySummary,
    EventGroupSummary,
    EventSummary,
    SubcategorySummary,
)
from betdex.markets.resources import MarketSummary
from betdex.resources import (
    BaseModel,
    DocumentReference,
    MatchBehavior,
    Meta,
    OffsetPageMeta,
    OrderStatus,
    PagedMeta,
    Response,
    Side,
)


@dataclass(kw_only=True, slots=True)
class CreateOrderRequest(BaseModel):
    """
    An order to place.
    """

    wallet_id: str
    market_id: str
    side: Side
    outcome_id: str
    price: float
    stake: float
    keep_when_in_play: bool
    match_behavior: MatchBehavior | None = None
    reference: str | None = None
    commission_rate_id: str | None = None


@dataclass(kw_only=True, slots=True)
class Order(BaseModel):
    """
    An order.
    """

    id: str
    app_id: str | None = None
    market: DocumentReference
    wallet_id: str | None = None
    side: Side
    outcome_id: str
    outcome_title: str
    price: float
    stake: float
    stake_unmatched: float
    stake_voided: float
    keep_when_in_play: bool
    created_at: datetime
    modified_at: datetime
    commission_rate_id: str | None = None
    reference: str | None = None
    status: OrderStatus
    match_behavior: MatchBehavior
    cancellation_reason: str | None = None

    @property
    def liability(self) -> float:
        """
        The most this order can lose if all of it matches: the stake for ``For``,
        ``stake * (price - 1)`` for ``Against`` (``stake`` is always the backer's stake).
        """
        return self.stake if self.side == "For" else self.stake * (self.price - 1)

    @property
    def stake_matched(self) -> float:
        """
        Stake matched so far: what is neither unmatched nor voided.
        """
        return self.stake - self.stake_unmatched - self.stake_voided


@dataclass(kw_only=True, slots=True)
class OrderFailure(BaseModel):
    """
    A refused order within a batch response; it doesn't say which request it was.
    """

    error_code: str
    error_message: str | None = None


@dataclass(kw_only=True, slots=True)
class OrderID(BaseModel):
    """
    An accepted order request's id within a batch response.
    """
    id: str


@dataclass(kw_only=True, slots=True)
class OrderSettled(BaseModel):
    """
    A settled order, from ``get_orders_historical``.
    """
    id: str
    app_id: str | None = None
    market: DocumentReference
    wallet_id: str | None = None
    side: Side
    outcome_id: str
    outcome_title: str
    price: float
    stake: float
    stake_unmatched: float
    stake_voided: float
    keep_when_in_play: bool
    created_at: datetime
    modified_at: datetime
    commission_rate_id: str | None = None
    reference: str | None = None
    status: OrderStatus
    match_behavior: MatchBehavior
    cancellation_reason: str | None = None
    settled_at: datetime
    event_expected_start_time: datetime | None = None


@dataclass(kw_only=True, slots=True)
class OrderSummary(BaseModel):
    """
    An order, as embedded in trade responses.
    """
    id: str
    market: DocumentReference
    side: Side
    outcome_id: str
    outcome_title: str | None = None
    price: float
    stake: float
    stake_unmatched: float | None = None
    stake_voided: float | None = None
    status: OrderStatus
    reference: str | None = None


@dataclass(kw_only=True, slots=True)
class Trade(BaseModel):
    """
    A fill: stake matched between an order and its counterparty.
    """
    id: str
    wallet_id: str | None = None
    market: DocumentReference
    order: DocumentReference
    side: Side
    outcome_id: str
    price: float
    stake: float
    profit_loss: float | None = None
    created_at: datetime
    modified_at: datetime | None = None


@dataclass(kw_only=True, slots=True)
class TradeSettled(BaseModel):
    """
    A settled trade, from ``get_trades_historical``.
    """
    id: str
    wallet_id: str | None = None
    market: DocumentReference
    order: DocumentReference
    side: Side
    outcome_id: str
    price: float
    stake: float
    profit_loss: float | None = None
    created_at: datetime
    modified_at: datetime | None = None
    settled_at: datetime
    event_expected_start_time: datetime | None = None


@dataclass(kw_only=True, slots=True)
class TradeSummary(BaseModel):
    """
    A trade, as embedded in order responses.
    """
    order: DocumentReference
    id: str
    price: float
    stake: float
    profit_loss: float | None = None
    created_at: datetime


@dataclass(kw_only=True, slots=True)
class OrderResponse(Response):
    """
    Orders with their related documents.
    """
    meta: Meta
    orders: list[Order] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    trades: list[TradeSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class PagedOrderResponse(Response):
    """
    A page of orders with their related documents.
    """
    meta: PagedMeta
    orders: list[Order] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    trades: list[TradeSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class BatchOrderResponse(Response):
    """
    The result of a batch placement.
    """

    meta: Meta
    orders: list[Order | OrderFailure] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    trades: list[TradeSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class BatchIDResponse(Response):
    """
    Per order request, an ``OrderID`` if accepted or an ``OrderFailure`` if not.
    """
    meta: Meta
    ids: list[OrderFailure | OrderID] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class OrdersResponseDocuments(BaseModel):
    """
    Orders with their related documents.
    """
    orders: list[Order] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    trades: list[TradeSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class OrdersSettledResponseDocuments(BaseModel):
    """
    Settled orders with their related documents.
    """
    orders: list[OrderSettled] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    trades: list[TradeSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class OffsetPageOrderResponse(Response):
    """
    A keyset page of orders.
    """
    meta: OffsetPageMeta
    documents: OrdersResponseDocuments


@dataclass(kw_only=True, slots=True)
class OffsetPageOrderHistoricalResponse(Response):
    """
    A keyset page of settled orders.
    """
    meta: OffsetPageMeta
    documents: OrdersSettledResponseDocuments


@dataclass(kw_only=True, slots=True)
class TradeResponse(Response):
    """
    Trades with their related documents.
    """
    meta: Meta
    trades: list[Trade] = field(default_factory=list)
    orders: list[OrderSummary] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class PagedTradeResponse(Response):
    """
    A page of trades with their related documents.
    """
    meta: PagedMeta
    trades: list[Trade] = field(default_factory=list)
    orders: list[OrderSummary] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class TradesHistoricalResponseDocuments(BaseModel):
    """
    Settled trades with their related documents.
    """
    trades: list[TradeSettled] = field(default_factory=list)
    orders: list[OrderSummary] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class OffsetPageTradeHistoricalResponse(Response):
    """
    A keyset page of settled trades.
    """
    meta: OffsetPageMeta
    documents: TradesHistoricalResponseDocuments
