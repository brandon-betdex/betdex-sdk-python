from collections.abc import Sequence
from datetime import datetime

from betdex.endpoints import Endpoints
from betdex.markets.resources import (
    MarketLiquiditiesResponse,
    MarketLiquidityResponse,
    MarketPriceLadderResponse,
    MarketResponse,
    MarketTypeResponse,
    OffsetPageMarketHistoricalResponse,
    PagedMarketPositionResponse,
    PagedMarketResponse,
)
from betdex.resources import (
    HistoricalQueryType,
    InPlayStatus,
    MarketStatus,
    Sort,
    SortDirection,
)


class MarketsEndpoints(Endpoints):
    """
    Market types, markets, prices, the price ladder and market positions.
    """

    def get_market_types(self) -> MarketTypeResponse:
        """
        Fetch all market types: ``GET /market-types``.

        :returns: Every market type.
        """
        return self.conn.call(MarketTypeResponse, "GET", "/market-types")

    def get_market_type(self, market_type_id: str) -> MarketTypeResponse:
        """
        Fetch one market type: ``GET /market-types/{id}``.

        :param market_type_id: Market type id, e.g. ``"Winner"``.
        :returns: The market type.
        """
        return self.conn.call(
            MarketTypeResponse, "GET", "/market-types/{id}",
            path_params={"id": market_type_id})

    def get_markets(
        self,
        *,
        ids: Sequence[str] | None = None,
        owner_app_ids: Sequence[str] | None = None,
        event_ids: Sequence[str] | None = None,
        market_type_ids: Sequence[str] | None = None,
        currency_ids: Sequence[str] | None = None,
        statuses: Sequence[MarketStatus] | None = None,
        in_play_statuses: Sequence[InPlayStatus] | None = None,
        from_date_time: datetime | None = None,
        to_date_time: datetime | None = None,
        published: bool | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedMarketResponse:
        """
        Fetch markets matching the filters: ``GET /markets``.

        :param ids: Market ids to match.
        :param owner_app_ids: Owning app ids to match.
        :param event_ids: Event ids to match.
        :param market_type_ids: Market type ids to match.
        :param currency_ids: Currency ids to match.
        :param statuses: Market statuses to match.
        :param in_play_statuses: In-play statuses to match.
        :param from_date_time: Window start.
        :param to_date_time: Window end.
        :param published: Match only published, or only unpublished, markets.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys on ``lockAt`` or ``settledAt``, e.g. ``["lockAt,asc"]``.
        :returns: One page of matching markets.
        """
        return self.conn.call(PagedMarketResponse, "GET", "/markets", params={
            "ids": ids,
            "ownerAppIds": owner_app_ids,
            "eventIds": event_ids,
            "marketTypeIds": market_type_ids,
            "currencyIds": currency_ids,
            "statuses": statuses,
            "inPlayStatuses": in_play_statuses,
            "fromDateTime": from_date_time,
            "toDateTime": to_date_time,
            "published": published,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_market(self, market_id: str) -> MarketResponse:
        """
        Fetch one market: ``GET /markets/{id}``.

        :param market_id: Market id.
        :returns: The market with its related documents.
        """
        return self.conn.call(
            MarketResponse, "GET", "/markets/{id}", path_params={"id": market_id})

    def get_markets_by_reference(
        self,
        source: str,
        reference: str,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedMarketResponse:
        """
        Fetch markets by external reference: ``GET /markets/by-reference/{source}/{reference}``.

        :param source: External reference source code.
        :param reference: Id within that source.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of matching markets.
        """
        return self.conn.call(
            PagedMarketResponse, "GET", "/markets/by-reference/{source}/{reference}",
            path_params={"source": source, "reference": reference},
            params={"page": page, "size": size, "sort": sort})

    def get_markets_historical(
        self,
        query_type: HistoricalQueryType,
        from_: datetime,
        to: datetime,
        *,
        event_id: str | None = None,
        offset: datetime | None = None,
        secondary_offset: int | None = None,
        limit: int | None = None,
        sort: SortDirection | None = None,
    ) -> OffsetPageMarketHistoricalResponse:
        """
        Fetch settled markets in a time window: ``GET /markets/historical``.

        Keyset-paged: pass the previous page's ``meta.next_offset`` back for the next.

        :param query_type: Whether the window applies to settlement or event start time.
        :param from_: Window start.
        :param to: Window end.
        :param event_id: Restrict to one event.
        :param offset: Cursor from the previous page's ``meta.next_offset``.
        :param secondary_offset: Cursor from the previous page's ``meta.next_offset``.
        :param limit: Rows per page.
        :param sort: ``"ASC"`` or ``"DESC"``.
        :returns: One page of settled markets.
        """
        return self.conn.call(
            OffsetPageMarketHistoricalResponse, "GET", "/markets/historical", params={
                "queryType": query_type,
                "from": from_,
                "to": to,
                "eventId": event_id,
                "offset": offset,
                "secondaryOffset": secondary_offset,
                "limit": limit,
                "sort": sort,
            })

    def get_market_prices(
        self,
        market_id: str,
        *,
        include_empty: bool | None = None,
        direct_only: bool | None = None,
    ) -> MarketLiquidityResponse:
        """
        Fetch one market's price book as a flat list: ``GET /markets/{id}/prices``.

        :param market_id: Market id.
        :param include_empty: Include price levels with no liquidity.
        :param direct_only: Exclude cross-matched liquidity.
        :returns: The market's price levels.
        """
        return self.conn.call(
            MarketLiquidityResponse, "GET", "/markets/{id}/prices",
            path_params={"id": market_id},
            params={"includeEmpty": include_empty, "directOnly": direct_only})

    def get_market_prices_v2(
        self, market_id: str, *, direct_only: bool | None = None,
    ) -> MarketLiquiditiesResponse:
        """
        Fetch one market's price book with totals: ``GET /markets/{id}/prices-v2``.

        :param market_id: Market id.
        :param direct_only: Exclude cross-matched liquidity.
        :returns: The market's price book.
        """
        return self.conn.call(
            MarketLiquiditiesResponse, "GET", "/markets/{id}/prices-v2",
            path_params={"id": market_id}, params={"directOnly": direct_only})

    def get_markets_prices(
        self,
        market_ids: Sequence[str],
        *,
        direct_only: bool | None = None,
    ) -> MarketLiquiditiesResponse:
        """
        Fetch price books for several markets: ``GET /market-prices``.

        :param market_ids: Market ids to match.
        :param direct_only: Exclude cross-matched liquidity.
        :returns: One price book per market.
        """
        return self.conn.call(MarketLiquiditiesResponse, "GET", "/market-prices", params={
            "marketIds": market_ids,
            "directOnly": direct_only,
        })

    def get_market_price_ladder(self) -> MarketPriceLadderResponse:
        """
        Fetch the prices orders may be placed at: ``GET /market-prices/ladder``.

        :returns: The price ladder.
        """
        return self.conn.call(MarketPriceLadderResponse, "GET", "/market-prices/ladder")

    def get_market_positions(
        self,
        market_id: str,
        *,
        wallet_ids: Sequence[str] | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedMarketPositionResponse:
        """
        Fetch positions on a market: ``GET /markets/{id}/positions``.

        :param market_id: Market id.
        :param wallet_ids: Wallet ids to match.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of positions.
        """
        return self.conn.call(
            PagedMarketPositionResponse, "GET", "/markets/{id}/positions",
            path_params={"id": market_id},
            params={"walletIds": wallet_ids, "page": page, "size": size, "sort": sort})
