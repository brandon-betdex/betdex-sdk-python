from dataclasses import dataclass, field
from datetime import datetime

from betdex.events.resources import (
    CategorySummary,
    EventGroupSummary,
    EventSummary,
    ParticipantSummary,
    SubcategorySummary,
)
from betdex.resources import (
    BaseModel,
    DocumentReference,
    ExternalReference,
    InPlayStatus,
    MarketAction,
    MarketStatus,
    Meta,
    OffsetPageMeta,
    PagedMeta,
    Range,
    Response,
    Side,
)


@dataclass(kw_only=True, slots=True)
class MarketType(BaseModel):
    """
    A kind of market, e.g. match result or total goals.
    """
    id: str
    outcomes_range: Range
    winners_range: Range
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class MarketTypeSummary(BaseModel):
    """
    A market type, as embedded in market responses.
    """
    id: str
    outcomes_range: Range
    winners_range: Range


@dataclass(kw_only=True, slots=True)
class MarketTypeResponse(Response):
    """
    Market types.
    """
    meta: Meta
    market_types: list[MarketType] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class MarketOutcomeSummary(BaseModel):
    """
    One outcome of a market.
    """
    id: str
    title: str
    ordering: int
    winner: bool | None = None
    participant: DocumentReference


@dataclass(kw_only=True, slots=True)
class Market(BaseModel):
    """
    A market on an event.

    ``in_play_status`` stays ``"InPlay"`` after settlement.

    :param market_value: The line, if any: one space-separated value per outcome for
        handicaps (``"-3.75 3.75"``), one shared value for totals (``"2.5"``).
    :param in_play_delay: Seconds orders are delayed while in play.
    :param market_lock_action: What happens to unmatched orders at lock.
    :param event_start_action: What happens to unmatched orders at event start.
    """
    id: str
    owner_app_id: str
    event: DocumentReference
    name: str
    market_type: DocumentReference
    market_value: str | None = None
    market_discriminator: str | None = None
    currency_id: str
    in_play_status: InPlayStatus
    in_play_delay: int | None = None
    cross_matching_enabled: bool
    published: bool
    suspended: bool
    lock_at: datetime
    settled_at: datetime | None = None
    market_lock_action: MarketAction
    event_start_action: MarketAction
    status: MarketStatus
    market_outcomes: DocumentReference
    external_references: DocumentReference
    created_at: datetime
    modified_at: datetime

    @property
    def is_in_play(self) -> bool:
        """
        Whether the market is open and trading in play. ``in_play_status`` alone
        stays ``InPlay`` after the market locks or settles.
        """
        return self.status == "Open" and self.in_play_status == "InPlay"


@dataclass(kw_only=True, slots=True)
class MarketSettled(BaseModel):
    """
    A settled market, from ``get_markets_historical``.
    """
    id: str
    owner_app_id: str
    event: DocumentReference
    name: str
    market_type: DocumentReference
    market_value: str | None = None
    market_discriminator: str | None = None
    currency_id: str
    in_play_status: InPlayStatus
    in_play_delay: int | None = None
    cross_matching_enabled: bool
    published: bool
    suspended: bool
    lock_at: datetime
    settled_at: datetime
    market_lock_action: MarketAction
    event_start_action: MarketAction
    status: MarketStatus
    market_outcomes: DocumentReference
    created_at: datetime
    modified_at: datetime
    event_expected_start_time: datetime


@dataclass(kw_only=True, slots=True)
class MarketSummary(BaseModel):
    """
    A market, as embedded in other responses.
    """
    id: str
    name: str
    in_play_status: InPlayStatus
    published: bool
    suspended: bool
    status: MarketStatus
    lock_at: datetime
    settled_at: datetime | None = None
    event: DocumentReference

    @property
    def is_in_play(self) -> bool:
        """
        Whether the market is open and trading in play. ``in_play_status`` alone
        stays ``InPlay`` after the market locks or settles.
        """
        return self.status == "Open" and self.in_play_status == "InPlay"


@dataclass(kw_only=True, slots=True)
class MarketResponse(Response):
    """
    Markets with their related documents.
    """
    meta: Meta
    markets: list[Market] = field(default_factory=list)
    market_types: list[MarketTypeSummary] = field(default_factory=list)
    market_outcomes: list[MarketOutcomeSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)
    participants: list[ParticipantSummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class PagedMarketResponse(Response):
    """
    A page of markets with their related documents.
    """
    meta: PagedMeta
    markets: list[Market] = field(default_factory=list)
    market_types: list[MarketTypeSummary] = field(default_factory=list)
    market_outcomes: list[MarketOutcomeSummary] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)
    participants: list[ParticipantSummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class MarketsHistoricalResponseDocuments(BaseModel):
    """
    Settled markets with their related documents.
    """
    markets: list[MarketSettled] = field(default_factory=list)
    events: list[EventSummary] = field(default_factory=list)
    event_groups: list[EventGroupSummary] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class OffsetPageMarketHistoricalResponse(Response):
    """
    A keyset page of settled markets.
    """
    meta: OffsetPageMeta
    documents: MarketsHistoricalResponseDocuments


@dataclass(kw_only=True, slots=True)
class MarketLiquidity(BaseModel):
    """
    Liquidity at one price on one side of one outcome.
    """
    side: Side
    outcome_id: str
    price: float
    amount: float
    matched: float


@dataclass(kw_only=True, slots=True)
class MarketLiquidities(BaseModel):
    """
    A market's price book.
    """
    market_id: str
    liquidity: float
    traded: float
    prices: list[MarketLiquidity] = field(default_factory=list)

    def available_to_back(self, outcome_id: str) -> list[MarketLiquidity]:
        """
        Prices ``outcome_id`` can be backed at now, best (highest) first: the
        resting ``Against`` levels.
        """
        levels = [p for p in self.prices
                  if p.outcome_id == outcome_id and p.side == "Against" and p.amount > 0]
        return sorted(levels, key=lambda p: p.price, reverse=True)

    def available_to_lay(self, outcome_id: str) -> list[MarketLiquidity]:
        """
        Prices ``outcome_id`` can be laid at now, best (lowest) first: the resting
        ``For`` levels.
        """
        levels = [p for p in self.prices
                  if p.outcome_id == outcome_id and p.side == "For" and p.amount > 0]
        return sorted(levels, key=lambda p: p.price)


@dataclass(kw_only=True, slots=True)
class MarketLiquidityResponse(Response):
    """
    One market's price book as a flat list of price levels.
    """
    meta: Meta
    prices: list[MarketLiquidity] = field(default_factory=list)

    def available_to_back(self, outcome_id: str) -> list[MarketLiquidity]:
        """
        Prices ``outcome_id`` can be backed at now, best (highest) first: the
        resting ``Against`` levels.
        """
        levels = [p for p in self.prices
                  if p.outcome_id == outcome_id and p.side == "Against" and p.amount > 0]
        return sorted(levels, key=lambda p: p.price, reverse=True)

    def available_to_lay(self, outcome_id: str) -> list[MarketLiquidity]:
        """
        Prices ``outcome_id`` can be laid at now, best (lowest) first: the resting
        ``For`` levels.
        """
        levels = [p for p in self.prices
                  if p.outcome_id == outcome_id and p.side == "For" and p.amount > 0]
        return sorted(levels, key=lambda p: p.price)


@dataclass(kw_only=True, slots=True)
class MarketLiquiditiesResponse(Response):
    """
    Price books, one per market.
    """
    meta: Meta
    prices: list[MarketLiquidities] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class MarketPosition(BaseModel):
    """
    A wallet's position on a market.
    """
    market: DocumentReference
    wallet_id: str | None = None
    exposures: dict[str, float] = field(default_factory=dict)


@dataclass(kw_only=True, slots=True)
class PagedMarketPositionResponse(Response):
    """
    A page of positions with their markets.
    """
    meta: PagedMeta
    positions: list[MarketPosition] = field(default_factory=list)
    markets: list[MarketSummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class MarketPriceLadder(BaseModel):
    """
    The prices orders may be placed at, ascending.
    """
    prices: list[float] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class MarketPriceLadderResponse(Response):
    """
    Price ladders.
    """
    meta: Meta
    market_price_ladders: list[MarketPriceLadder] = field(default_factory=list)
