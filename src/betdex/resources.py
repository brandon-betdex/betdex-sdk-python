from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from betdex.utils import decode, encode

CurrencyType = Literal["Crypto", "Fiat"]
Side = Literal["For", "Against"]
MatchBehavior = Literal["RetainUnmatched", "CancelUnmatched"]
InPlayStatus = Literal["NotApplicable", "PrePlay", "InPlay"]
MarketAction = Literal["None", "CancelUnmatchedLiquidity"]
ParticipantType = Literal["Individual", "Team"]
EventStarting = Literal["Live", "Today", "Later", "Range"]
HistoricalQueryType = Literal["SettledDate", "EventStartDate"]
WalletType = Literal["Commission", "MarketEscrow", "System", "User"]
PositionFilter = Literal["Active", "Settled"]
SortDirection = Literal["ASC", "DESC"]
Sort = Sequence[str]

MarketStatus = Literal[
    "Initializing", "Open", "Locking", "Locked", "Settling", "Settled",
    "Voiding", "Voided", "Closed",
]

OrderStatus = Literal[
    "Cancelled", "Failed", "Matched", "PartiallyMatched", "Pending", "Unmatched",
    "Won", "Lost", "Voided", "HalfWon", "HalfLost", "Push",
]

TransactionCode = Literal[
    "Deposit", "Withdrawal", "TradeCreation", "TradeVoid", "TradeWin",
    "WalletToWallet", "Commission", "MarketPositionVoid", "MarketPositionPayout",
    "MarketPositionRefund", "ManualDebit", "ManualCredit", "SettlementResidual",
]


@dataclass(kw_only=True, slots=True)
class BaseModel:
    """
    Base class for every model.
    """

    @classmethod
    def from_json(cls: Any, data: dict[str, Any]) -> Any:
        """
        Build the model from a decoded JSON object.

        :param data: Object as the API returns it; undeclared keys are ignored.
        :returns: The model.
        """
        return decode(cls, data)

    def to_json(self) -> dict[str, Any]:
        """
        Convert the model to a JSON-ready dict.

        :returns: The non-``None`` fields, with camelCase keys.
        """
        return encode(self)


@dataclass(kw_only=True, slots=True)
class Response(BaseModel):
    """
    Base class for a top-level API response.

    :param raw: The decoded body, for fields the model does not declare.

    :ivar sent_at: When the request was sent (UTC).
    :ivar received_at: When the response arrived (UTC).
    :ivar latency_ms: Milliseconds from sending to the response, timed on a
        monotonic clock, so not exactly ``received_at - sent_at``.
    """
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
    sent_at: datetime = field(init=False, repr=False, compare=False)
    received_at: datetime = field(init=False, repr=False, compare=False)
    latency_ms: float = field(init=False, repr=False, compare=False)


@dataclass(kw_only=True, slots=True)
class PageMeta(BaseModel):
    """
    Position of a page-numbered response (``_meta._page``); pages are zero-based.
    """
    page_number: int
    page_size: int
    total_elements: int
    total_pages: int


@dataclass(kw_only=True, slots=True)
class Meta(BaseModel):
    """
    Response metadata (``_meta``).

    :param primary_document: Name of the list the response is about, e.g. ``"orders"``.
    :param count: Number of primary documents in this response.
    :param page: Paging position, on paged endpoints.
    """
    primary_document: str
    count: int
    page: PageMeta | None = None


@dataclass(kw_only=True, slots=True)
class PagedMeta(BaseModel):
    """
    Metadata of a page-numbered response (``_meta``), where ``page`` is always present.

    :param primary_document: Name of the list the response is about, e.g. ``"orders"``.
    :param count: Number of primary documents in this response.
    :param page: Paging position.
    """
    primary_document: str
    count: int
    page: PageMeta


@dataclass(kw_only=True, slots=True)
class OffsetRequest(BaseModel):
    """
    A keyset-paging cursor (spec name ``OffsetRequestInstantLong``).

    Pass ``offset`` and ``secondary_offset`` from ``next_offset`` back to get the next page.
    """
    offset: datetime | None = None
    secondary_offset: int | None = None
    limit: int
    sort: SortDirection


@dataclass(kw_only=True, slots=True)
class OffsetPageMeta(BaseModel):
    """
    Metadata of a keyset-paged response (spec name ``OffsetPageMetaInstantLong``).

    :param offset: The cursor this page was fetched with.
    :param next_offset: The cursor for the next page; ``None`` on the last page.
    """
    primary_document: str
    count: int
    offset: OffsetRequest
    next_offset: OffsetRequest | None = None


@dataclass(kw_only=True, slots=True)
class DocumentReference(BaseModel):
    """
    A pointer from one document to related ones.

    :param ref: ``"<list>.<key>"``, e.g. ``"events.id"``: the response's ``events``
        list, matched on ``id``.
    :param ids: Ids of the related documents.
    """
    ref: str
    ids: list[str] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class ExternalReference(BaseModel):
    """
    An id for a BetDEX document in an external source's namespace.
    """
    id: int
    source: str
    external_reference: str


@dataclass(kw_only=True, slots=True)
class Range(BaseModel):
    """
    An inclusive integer range.
    """
    min: int
    max: int


@dataclass(kw_only=True, slots=True)
class IDResponse(Response):
    """
    A list of document ids.
    """
    meta: Meta
    ids: list[str] = field(default_factory=list)
