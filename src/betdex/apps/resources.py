from dataclasses import dataclass, field
from datetime import datetime

from betdex.resources import BaseModel, Meta, Response


@dataclass(kw_only=True, slots=True)
class CommissionRate(BaseModel):
    """
    A commission rate an app charges on winnings.
    """
    id: str
    rate: float
    created_at: datetime | None = None


@dataclass(kw_only=True, slots=True)
class CommissionRateResponse(Response):
    """
    An app's commission rates.
    """
    meta: Meta
    commission_rates: list[CommissionRate] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class Session(BaseModel):
    """
    A session's bearer tokens.
    """
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


@dataclass(kw_only=True, slots=True)
class SessionResponse(Response):
    """
    Sessions created or refreshed.
    """
    meta: Meta
    sessions: list[Session] = field(default_factory=list)
