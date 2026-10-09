from dataclasses import dataclass, field
from datetime import datetime

from betdex.resources import (
    BaseModel,
    Meta,
    PagedMeta,
    Response,
    TransactionCode,
    WalletType,
)


@dataclass(kw_only=True, slots=True)
class WalletBalance(BaseModel):
    """
    A wallet's balance in one currency.
    """
    currency_id: str
    balance: float
    balance_available: float
    overdraft: float
    unmatched_exposure: float


@dataclass(kw_only=True, slots=True)
class Wallet(BaseModel):
    """
    A wallet and its balances.
    """
    id: str
    app_id: str
    type: WalletType
    reference: str | None = None
    description: str | None = None
    balances: list[WalletBalance] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class WalletResponse(Response):
    """
    Wallets.
    """
    meta: Meta
    wallets: list[Wallet] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class PagedWalletResponse(Response):
    """
    A page of wallets.
    """
    meta: PagedMeta
    wallets: list[Wallet] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class Transaction(BaseModel):
    """
    A wallet ledger entry.
    """
    transaction_id: str
    code: TransactionCode
    wallet_id: str
    currency_id: str
    amount: float
    description: str | None = None
    created_at: datetime


@dataclass(kw_only=True, slots=True)
class PagedTransactionResponse(Response):
    """
    A page of ledger entries.
    """
    meta: PagedMeta
    transactions: list[Transaction] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class WalletMetric(BaseModel):
    """
    Order total and count for one state.
    """
    total: float
    count: int


@dataclass(kw_only=True, slots=True)
class WalletMetrics(BaseModel):
    """
    A wallet's order totals and counts by state over a time window.
    """
    open: WalletMetric
    matched: WalletMetric
    cancelled: WalletMetric
    settled: WalletMetric
    voided: WalletMetric


@dataclass(kw_only=True, slots=True)
class WalletMetricsResponse(Response):
    """
    A wallet's order metrics.
    """
    meta: Meta
    wallet_metrics: WalletMetrics


@dataclass(kw_only=True, slots=True)
class TransferResponse(Response):
    """
    The result of a funds transfer, e.g. a faucet credit.
    """
    meta: Meta | None = None
    transaction_id: str
    wallet: Wallet
