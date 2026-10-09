from collections.abc import Sequence
from datetime import datetime

from betdex.endpoints import Endpoints
from betdex.events.resources import (
    CategoryResponse,
    EventGroupResponse,
    EventParticipantsResponse,
    EventResponse,
    PagedEventResponse,
    ParticipantsResponse,
    SubcategoryResponse,
)
from betdex.resources import EventStarting, Sort


class EventsEndpoints(Endpoints):
    """
    Categories, subcategories, event groups, events and participants.
    """

    def get_categories(self) -> CategoryResponse:
        """
        Fetch all event categories: ``GET /categories``.

        :returns: Every category.
        """
        return self.conn.call(CategoryResponse, "GET", "/categories")

    def get_category(self, category_id: str) -> CategoryResponse:
        """
        Fetch one event category: ``GET /categories/{id}``.

        :param category_id: Category to fetch.
        :returns: The category.
        """
        return self.conn.call(
            CategoryResponse, "GET", "/categories/{id}",
            path_params={"id": category_id})

    def get_subcategories(
        self, category_ids: Sequence[str] | None = None,
    ) -> SubcategoryResponse:
        """
        Fetch subcategories: ``GET /subcategories``.

        :param category_ids: Category ids to match; all if omitted.
        :returns: Matching subcategories.
        """
        return self.conn.call(
            SubcategoryResponse, "GET", "/subcategories",
            params={"categoryIds": category_ids})

    def get_subcategory(self, subcategory_id: str) -> SubcategoryResponse:
        """
        Fetch one subcategory: ``GET /subcategories/{id}``.

        :param subcategory_id: Subcategory to fetch.
        :returns: The subcategory.
        """
        return self.conn.call(
            SubcategoryResponse, "GET", "/subcategories/{id}",
            path_params={"id": subcategory_id})

    def get_subcategory_by_reference(
        self, source: str, reference: str,
    ) -> SubcategoryResponse:
        """
        Fetch a subcategory by external reference:
        ``GET /subcategories/by-reference/{source}/{reference}``.

        :param source: External reference source code.
        :param reference: Id within that source.
        :returns: The matching subcategory.
        """
        return self.conn.call(
            SubcategoryResponse, "GET", "/subcategories/by-reference/{source}/{reference}",
            path_params={"source": source, "reference": reference})

    def get_subcategory_participants(self, subcategory_id: str) -> ParticipantsResponse:
        """
        Fetch a subcategory's participants: ``GET /subcategories/{id}/participants``.

        :param subcategory_id: Subcategory whose participants to fetch.
        :returns: The subcategory's participants.
        """
        return self.conn.call(
            ParticipantsResponse, "GET", "/subcategories/{id}/participants",
            path_params={"id": subcategory_id})

    def get_event_groups(
        self, subcategory_ids: Sequence[str] | None = None,
    ) -> EventGroupResponse:
        """
        Fetch event groups: ``GET /event-groups``.

        :param subcategory_ids: Subcategory ids to match; all if omitted.
        :returns: Matching event groups.
        """
        return self.conn.call(
            EventGroupResponse, "GET", "/event-groups",
            params={"subcategoryIds": subcategory_ids})

    def get_event_group(self, event_group_id: str) -> EventGroupResponse:
        """
        Fetch one event group: ``GET /event-groups/{id}``.

        :param event_group_id: Event group to fetch.
        :returns: The event group.
        """
        return self.conn.call(
            EventGroupResponse, "GET", "/event-groups/{id}",
            path_params={"id": event_group_id})

    def get_event_group_by_reference(
        self, source: str, reference: str,
    ) -> EventGroupResponse:
        """
        Fetch an event group by external reference:
        ``GET /event-groups/by-reference/{source}/{reference}``.

        :param source: External reference source code.
        :param reference: Id within that source.
        :returns: The matching event group.
        """
        return self.conn.call(
            EventGroupResponse, "GET", "/event-groups/by-reference/{source}/{reference}",
            path_params={"source": source, "reference": reference})

    def get_events(
        self,
        *,
        ids: Sequence[str] | None = None,
        owner_app_ids: Sequence[str] | None = None,
        category_ids: Sequence[str] | None = None,
        subcategory_ids: Sequence[str] | None = None,
        event_group_ids: Sequence[str] | None = None,
        starting: EventStarting | None = None,
        from_date_time: datetime | None = None,
        to_date_time: datetime | None = None,
        active: bool | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedEventResponse:
        """
        Fetch events matching the filters: ``GET /events``.

        :param ids: Event ids to match.
        :param owner_app_ids: Owning app ids to match.
        :param category_ids: Category ids to match.
        :param subcategory_ids: Subcategory ids to match.
        :param event_group_ids: Event group ids to match.
        :param starting: Start-time window; ``"Range"`` uses ``from_date_time`` and
            ``to_date_time``.
        :param from_date_time: Start of the ``"Range"`` window.
        :param to_date_time: End of the ``"Range"`` window.
        :param active: Match only active (``True``) or inactive (``False``) events.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["expectedStartTime,asc"]``.
        :returns: One page of matching events.
        """
        return self.conn.call(PagedEventResponse, "GET", "/events", params={
            "ids": ids,
            "ownerAppIds": owner_app_ids,
            "categoryIds": category_ids,
            "subcategoryIds": subcategory_ids,
            "eventGroupIds": event_group_ids,
            "starting": starting,
            "fromDateTime": from_date_time,
            "toDateTime": to_date_time,
            "active": active,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_event(self, event_id: str) -> EventResponse:
        """
        Fetch one event: ``GET /events/{id}``.

        :param event_id: Event to fetch.
        :returns: The event with its related documents.
        """
        return self.conn.call(
            EventResponse, "GET", "/events/{id}", path_params={"id": event_id})

    def get_events_by_reference(
        self,
        source: str,
        reference: str,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedEventResponse:
        """
        Fetch events by external reference:
        ``GET /events/by-reference/{source}/{reference}``.

        :param source: External reference source code.
        :param reference: Id within that source.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["expectedStartTime,asc"]``.
        :returns: One page of matching events.
        """
        return self.conn.call(
            PagedEventResponse, "GET", "/events/by-reference/{source}/{reference}",
            path_params={"source": source, "reference": reference},
            params={"page": page, "size": size, "sort": sort})

    def get_event_participants(self, event_id: str) -> EventParticipantsResponse:
        """
        Fetch an event's participants: ``GET /events/{id}/participants``.

        :param event_id: Event whose participants to fetch.
        :returns: The event's participants.
        """
        return self.conn.call(
            EventParticipantsResponse, "GET", "/events/{id}/participants",
            path_params={"id": event_id})

    def get_participants_by_reference(
        self, source: str, reference: str,
    ) -> ParticipantsResponse:
        """
        Fetch participants by external reference:
        ``GET /participants/by-reference/{source}/{reference}``.

        :param source: External reference source code.
        :param reference: Id within that source.
        :returns: The matching participants.
        """
        return self.conn.call(
            ParticipantsResponse, "GET", "/participants/by-reference/{source}/{reference}",
            path_params={"source": source, "reference": reference})
