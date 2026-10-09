from dataclasses import dataclass, field
from datetime import datetime

from betdex.resources import BaseModel, Meta, Response


@dataclass(kw_only=True, slots=True)
class Heartbeat(BaseModel):
    """
    An app's dead-man's switch.
    """
    app_id: str
    active: bool
    timeout_ms: int
    last_seen_at: datetime


@dataclass(kw_only=True, slots=True)
class HeartbeatResponse(Response):
    """
    An app's heartbeat.
    """
    meta: Meta
    heartbeats: list[Heartbeat] = field(default_factory=list)
