from dataclasses import dataclass, field
from datetime import datetime

from betdex.resources import (
    BaseModel,
    DocumentReference,
    ExternalReference,
    Meta,
    PagedMeta,
    ParticipantType,
    Response,
)


@dataclass(kw_only=True, slots=True)
class Category(BaseModel):
    """
    A top-level grouping, e.g. a sport.
    """
    id: str
    name: str
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class CategorySummary(BaseModel):
    """
    A category as referenced from another document.
    """
    id: str
    name: str


@dataclass(kw_only=True, slots=True)
class CategorySummaryWithDates(BaseModel):
    """
    A category summary with its timestamps.
    """
    id: str
    name: str
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class CategoryResponse(Response):
    """
    Event categories.
    """
    meta: Meta
    categories: list[Category] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class Subcategory(BaseModel):
    """
    A grouping within a category, e.g. a competition type.
    """
    id: str
    external_references: DocumentReference
    name: str
    category: DocumentReference
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class SubcategorySummary(BaseModel):
    """
    A subcategory as referenced from another document.
    """
    id: str
    name: str
    category: DocumentReference


@dataclass(kw_only=True, slots=True)
class SubcategorySummaryWithDates(BaseModel):
    """
    A subcategory summary with its timestamps.
    """
    id: str
    name: str
    category: DocumentReference
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class SubcategoryResponse(Response):
    """
    Subcategories with their related documents.
    """
    meta: Meta
    subcategories: list[Subcategory] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class EventGroup(BaseModel):
    """
    A grouping of events within a subcategory, e.g. a league.
    """
    id: str
    external_references: DocumentReference
    name: str
    subcategory: DocumentReference
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class EventGroupSummary(BaseModel):
    """
    An event group as referenced from another document.
    """
    id: str
    name: str
    subcategory: DocumentReference


@dataclass(kw_only=True, slots=True)
class EventGroupSummaryWithDates(BaseModel):
    """
    An event group summary with its timestamps.
    """
    id: str
    name: str
    subcategory: DocumentReference
    created_at: datetime
    modified_at: datetime


@dataclass(kw_only=True, slots=True)
class EventGroupResponse(Response):
    """
    Event groups with their related documents.
    """
    meta: Meta
    event_groups: list[EventGroup] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)
    subcategories: list[SubcategorySummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class Participant(BaseModel):
    """
    A team or individual taking part in events.
    """
    id: str
    external_references: DocumentReference
    code: str
    name: str
    type: ParticipantType
    active: bool


@dataclass(kw_only=True, slots=True)
class ParticipantSummary(BaseModel):
    """
    A participant as referenced from another document.
    """
    id: str
    code: str
    name: str
    type: ParticipantType
    active: bool


@dataclass(kw_only=True, slots=True)
class ParticipantsResponse(Response):
    """
    Participants with their external references.
    """
    meta: Meta
    participants: list[Participant] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class EventParticipant(BaseModel):
    """
    A participant as listed on an event. Deprecated in the API spec.
    """
    id: str
    code: str
    name: str
    type: ParticipantType


@dataclass(kw_only=True, slots=True)
class EventParticipantsResponse(Response):
    """
    An event's participants.
    """
    meta: Meta
    participants: list[EventParticipant] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class Event(BaseModel):
    """
    A fixture markets are offered on.
    """
    id: str
    owner_app_id: str
    event_group: DocumentReference
    name: str
    code: str
    active: bool
    expected_start_time: datetime
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    created_at: datetime
    modified_at: datetime
    participants: DocumentReference
    external_references: DocumentReference


@dataclass(kw_only=True, slots=True)
class EventSummary(BaseModel):
    """
    An event as referenced from another document.
    """
    id: str
    event_group: DocumentReference
    name: str
    code: str
    expected_start_time: datetime
    active: bool


@dataclass(kw_only=True, slots=True)
class EventResponse(Response):
    """
    Events with their related documents.
    """
    meta: Meta
    events: list[Event] = field(default_factory=list)
    event_groups: list[EventGroupSummaryWithDates] = field(default_factory=list)
    subcategories: list[SubcategorySummaryWithDates] = field(default_factory=list)
    categories: list[CategorySummaryWithDates] = field(default_factory=list)
    participants: list[EventParticipant] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class PagedEventResponse(Response):
    """
    One page of events; ``meta.page`` holds the position.
    """
    meta: PagedMeta
    events: list[Event] = field(default_factory=list)
    event_groups: list[EventGroupSummaryWithDates] = field(default_factory=list)
    subcategories: list[SubcategorySummaryWithDates] = field(default_factory=list)
    categories: list[CategorySummaryWithDates] = field(default_factory=list)
    participants: list[EventParticipant] = field(default_factory=list)
    external_references: list[ExternalReference] = field(default_factory=list)
