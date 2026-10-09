from collections.abc import Sequence
from datetime import datetime

from betdex.endpoints import Endpoints
from betdex.orders.resources import (
    BatchIDResponse,
    BatchOrderResponse,
    CreateOrderRequest,
    OffsetPageOrderHistoricalResponse,
    OffsetPageOrderResponse,
    OffsetPageTradeHistoricalResponse,
    OrderResponse,
    PagedOrderResponse,
    PagedTradeResponse,
    TradeResponse,
)
from betdex.resources import (
    HistoricalQueryType,
    IDResponse,
    MatchBehavior,
    OrderStatus,
    Side,
    Sort,
    SortDirection,
)
from betdex.utils import encode


class OrdersEndpoints(Endpoints):
    """
    Orders and trades.
    """

    def get_orders(
        self,
        *,
        ids: Sequence[str] | None = None,
        app_ids: Sequence[str] | None = None,
        event_ids: Sequence[str] | None = None,
        market_ids: Sequence[str] | None = None,
        wallet_ids: Sequence[str] | None = None,
        references: Sequence[str] | None = None,
        statuses: Sequence[OrderStatus] | None = None,
        from_stake: float | None = None,
        to_stake: float | None = None,
        from_created_at: datetime | None = None,
        to_created_at: datetime | None = None,
        match_behavior: MatchBehavior | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedOrderResponse:
        """
        Fetch orders matching the filters: ``GET /orders``.

        The API requires at least one of ``ids``, ``app_ids``, ``event_ids``,
        ``market_ids``, ``wallet_ids`` or ``references``.

        :param ids: Order ids to match.
        :param app_ids: App ids to match.
        :param event_ids: Event ids to match.
        :param market_ids: Market ids to match.
        :param wallet_ids: Wallet ids to match.
        :param references: Client references to match; the API requires ``app_ids`` with it.
        :param statuses: Order statuses to match.
        :param from_stake: Minimum stake.
        :param to_stake: Maximum stake.
        :param from_created_at: Created at or after.
        :param to_created_at: Created at or before.
        :param match_behavior: Match behaviour to match.
        :param page: Zero-based page number.
        :param size: Page size, at most 500 here.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of matching orders.
        """
        return self.conn.call(PagedOrderResponse, "GET", "/orders", params={
            "ids": ids,
            "appIds": app_ids,
            "eventIds": event_ids,
            "marketIds": market_ids,
            "walletIds": wallet_ids,
            "references": references,
            "statuses": statuses,
            "fromStake": from_stake,
            "toStake": to_stake,
            "fromCreatedAt": from_created_at,
            "toCreatedAt": to_created_at,
            "matchBehavior": match_behavior,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_order(self, order_id: str) -> OrderResponse:
        """
        Fetch one order: ``GET /orders/{id}``.

        :param order_id: Order id.
        :returns: The order with its related documents.
        """
        return self.conn.call(
            OrderResponse, "GET", "/orders/{id}", path_params={"id": order_id})

    def get_order_by_reference(self, reference: str) -> OrderResponse:
        """
        Fetch one order by client reference: ``GET /orders/by-reference/{reference}``.

        The API can't look up references containing ``/`` or ``\\`` (400).

        :param reference: The order's client reference.
        :returns: The order with its related documents.
        """
        return self.conn.call(
            OrderResponse, "GET", "/orders/by-reference/{reference}",
            path_params={"reference": reference})

    def get_order_trades(
        self,
        order_id: str,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> TradeResponse:
        """
        Fetch one order's fills: ``GET /orders/{id}/trades``.

        :param order_id: Order id.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: The order's trades.
        """
        return self.conn.call(
            TradeResponse, "GET", "/orders/{id}/trades",
            path_params={"id": order_id},
            params={"page": page, "size": size, "sort": sort})

    def get_orders_settled(
        self,
        from_settled_at: datetime,
        to_settled_at: datetime,
        *,
        wallet_id: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedOrderResponse:
        """
        Fetch orders settled in a time window: ``GET /orders/settled``.

        :param from_settled_at: Window start.
        :param to_settled_at: Window end.
        :param wallet_id: Restrict to one wallet; not defaulted from the connection.
        :param page: Zero-based page number.
        :param size: Page size, at most 500 here.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of settled orders.
        """
        return self.conn.call(PagedOrderResponse, "GET", "/orders/settled", params={
            "fromSettledAt": from_settled_at,
            "toSettledAt": to_settled_at,
            "walletId": wallet_id,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_orders_historical(
        self,
        query_type: HistoricalQueryType,
        from_: datetime,
        to: datetime,
        *,
        wallet_id: str | None = None,
        market_id: str | None = None,
        offset: datetime | None = None,
        secondary_offset: int | None = None,
        limit: int | None = None,
        sort: SortDirection | None = None,
    ) -> OffsetPageOrderHistoricalResponse:
        """
        Fetch a wallet's won, lost or voided orders in a time window: ``GET /orders/historical``.

        Keyset-paged: pass the previous page's ``meta.next_offset`` back for the next.

        :param query_type: Whether the window applies to settlement or event start time.
        :param from_: Window start.
        :param to: Window end.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param market_id: Restrict to one market.
        :param offset: Cursor from the previous page's ``meta.next_offset``.
        :param secondary_offset: Cursor from the previous page's ``meta.next_offset``.
        :param limit: Rows per page.
        :param sort: ``"ASC"`` or ``"DESC"``.
        :returns: One page of settled orders.
        """
        return self.conn.call(
            OffsetPageOrderHistoricalResponse, "GET", "/orders/historical", params={
                "walletId": self.conn.resolve_wallet_id(wallet_id),
                "queryType": query_type,
                "from": from_,
                "to": to,
                "marketId": market_id,
                "offset": offset,
                "secondaryOffset": secondary_offset,
                "limit": limit,
                "sort": sort,
            })

    def get_orders_cancelled(
        self,
        from_created_at: datetime,
        to_created_at: datetime,
        *,
        wallet_id: str | None = None,
        market_id: str | None = None,
        offset: datetime | None = None,
        secondary_offset: int | None = None,
        limit: int | None = None,
        sort: SortDirection | None = None,
    ) -> OffsetPageOrderResponse:
        """
        Fetch a wallet's cancelled and failed orders: ``GET /orders/cancelled``.

        Keyset-paged: pass the previous page's ``meta.next_offset`` back for the next.

        :param from_created_at: Created at or after.
        :param to_created_at: Created at or before.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param market_id: Restrict to one market.
        :param offset: Cursor from the previous page's ``meta.next_offset``.
        :param secondary_offset: Cursor from the previous page's ``meta.next_offset``.
        :param limit: Rows per page.
        :param sort: ``"ASC"`` or ``"DESC"``.
        :returns: One page of cancelled and failed orders.
        """
        return self.conn.call(OffsetPageOrderResponse, "GET", "/orders/cancelled", params={
            "walletId": self.conn.resolve_wallet_id(wallet_id),
            "fromCreatedAt": from_created_at,
            "toCreatedAt": to_created_at,
            "marketId": market_id,
            "offset": offset,
            "secondaryOffset": secondary_offset,
            "limit": limit,
            "sort": sort,
        })

    def get_market_orders(
        self,
        market_id: str,
        *,
        wallet_ids: Sequence[str] | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedOrderResponse:
        """
        Fetch orders on a market: ``GET /markets/{id}/orders``.

        :param market_id: Market id.
        :param wallet_ids: Wallet ids to match.
        :param page: Zero-based page number.
        :param size: Page size, at most 500 here.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of orders.
        """
        return self.conn.call(
            PagedOrderResponse, "GET", "/markets/{id}/orders",
            path_params={"id": market_id},
            params={"walletIds": wallet_ids, "page": page, "size": size, "sort": sort})

    def create_order(
        self,
        market_id: str,
        outcome_id: str,
        side: Side,
        price: float,
        stake: float,
        *,
        keep_when_in_play: bool,
        wallet_id: str | None = None,
        match_behavior: MatchBehavior | None = None,
        reference: str | None = None,
        commission_rate_id: str | None = None,
    ) -> OrderResponse:
        """
        Place one order: ``POST /orders``.

        :param market_id: Market to bet on.
        :param outcome_id: Outcome to bet on.
        :param side: ``"For"`` backs the outcome, ``"Against"`` lays it.
        :param price: Decimal odds, on the price ladder.
        :param stake: Amount staked.
        :param keep_when_in_play: Keep the unmatched part when the market goes in play.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param match_behavior: ``"CancelUnmatched"`` cancels what doesn't match at once.
        :param reference: Client-chosen id, echoed back on the order.
        :param commission_rate_id: Commission rate to apply, if not the default.
        :returns: The created order.
        """
        order = CreateOrderRequest(
            wallet_id=self.conn.resolve_wallet_id(wallet_id),
            market_id=market_id,
            side=side,
            outcome_id=outcome_id,
            price=price,
            stake=stake,
            keep_when_in_play=keep_when_in_play,
            match_behavior=match_behavior,
            reference=reference,
            commission_rate_id=commission_rate_id,
        )
        return self.conn.call(OrderResponse, "POST", "/orders", json=encode(order))

    def create_orders(self, orders: Sequence[CreateOrderRequest]) -> BatchOrderResponse:
        """
        Place several orders in one call: ``POST /orders/batch``.

        Each order succeeds or fails on its own; see ``BatchOrderResponse``.

        :param orders: Orders to place, at most ``MAX_BATCH_SIZE``; see ``utils.batch`` for more.
        :returns: One ``Order`` or ``OrderFailure`` per request.
        """
        return self.conn.call(
            BatchOrderResponse, "POST", "/orders/batch",
            json={"requests": encode(list(orders))})

    def create_order_request(
        self,
        market_id: str,
        outcome_id: str,
        side: Side,
        price: float,
        stake: float,
        *,
        keep_when_in_play: bool,
        wallet_id: str | None = None,
        match_behavior: MatchBehavior | None = None,
        reference: str | None = None,
        commission_rate_id: str | None = None,
    ) -> IDResponse:
        """
        Submit one order for asynchronous processing: ``POST /order-requests``.

        "Coming soon" in the API spec.

        :param market_id: Market to bet on.
        :param outcome_id: Outcome to bet on.
        :param side: ``"For"`` backs the outcome, ``"Against"`` lays it.
        :param price: Decimal odds, on the price ladder.
        :param stake: Amount staked.
        :param keep_when_in_play: Keep the unmatched part when the market goes in play.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param match_behavior: ``"CancelUnmatched"`` cancels what doesn't match at once.
        :param reference: Client-chosen id, echoed back on the order.
        :param commission_rate_id: Commission rate to apply, if not the default.
        :returns: The order request's id.
        """
        order = CreateOrderRequest(
            wallet_id=self.conn.resolve_wallet_id(wallet_id),
            market_id=market_id,
            side=side,
            outcome_id=outcome_id,
            price=price,
            stake=stake,
            keep_when_in_play=keep_when_in_play,
            match_behavior=match_behavior,
            reference=reference,
            commission_rate_id=commission_rate_id,
        )
        return self.conn.call(IDResponse, "POST", "/order-requests", json=encode(order))

    def create_order_requests(
        self, orders: Sequence[CreateOrderRequest],
    ) -> BatchIDResponse:
        """
        Submit several orders for asynchronous processing: ``POST /order-requests/batch``.

        "Coming soon" in the API spec.

        :param orders: Orders to submit, at most ``MAX_BATCH_SIZE``; see ``utils.batch`` for more.
        :returns: One ``OrderID`` or ``OrderFailure`` per request.
        """
        return self.conn.call(
            BatchIDResponse, "POST", "/order-requests/batch",
            json={"requests": encode(list(orders))})

    def cancel_orders(
        self,
        *,
        order_ids: Sequence[str] | None = None,
        market_ids: Sequence[str] | None = None,
        event_ids: Sequence[str] | None = None,
        wallet_ids: Sequence[str] | None = None,
    ) -> IDResponse:
        """
        Cancel unmatched orders matching any of the filters: ``POST /orders/cancel-v2``.

        Not in the published spec. ``wallet_ids=[wallet]`` cancels everything resting in a wallet.

        :param order_ids: Order ids to cancel.
        :param market_ids: Cancel orders on these markets.
        :param event_ids: Cancel orders on these events.
        :param wallet_ids: Cancel orders in these wallets.
        :returns: Ids actually cancelled; any requested id missing from it was not.
        """
        body = {
            "orderIds": order_ids,
            "marketIds": market_ids,
            "eventIds": event_ids,
            "walletIds": wallet_ids,
        }
        return self.conn.call(
            IDResponse, "POST", "/orders/cancel-v2",
            json={k: list(v) for k, v in body.items() if v is not None})

    def get_trades(
        self,
        *,
        market_ids: Sequence[str] | None = None,
        wallet_ids: Sequence[str] | None = None,
        order_ids: Sequence[str] | None = None,
        from_created_at: datetime | None = None,
        to_created_at: datetime | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedTradeResponse:
        """
        Fetch trades matching the filters: ``GET /trades``.

        :param market_ids: Market ids to match.
        :param wallet_ids: Wallet ids to match.
        :param order_ids: Order ids to match.
        :param from_created_at: Created at or after.
        :param to_created_at: Created at or before.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of matching trades.
        """
        return self.conn.call(PagedTradeResponse, "GET", "/trades", params={
            "marketIds": market_ids,
            "walletIds": wallet_ids,
            "orderIds": order_ids,
            "fromCreatedAt": from_created_at,
            "toCreatedAt": to_created_at,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_trade(self, trade_id: str) -> TradeResponse:
        """
        Fetch one trade: ``GET /trades/{id}``.

        :param trade_id: Trade id.
        :returns: The trade with its related documents.
        """
        return self.conn.call(
            TradeResponse, "GET", "/trades/{id}", path_params={"id": trade_id})

    def get_trades_historical(
        self,
        query_type: HistoricalQueryType,
        from_: datetime,
        to: datetime,
        *,
        wallet_id: str | None = None,
        market_id: str | None = None,
        offset: datetime | None = None,
        secondary_offset: int | None = None,
        limit: int | None = None,
        sort: SortDirection | None = None,
    ) -> OffsetPageTradeHistoricalResponse:
        """
        Fetch a wallet's won, lost or voided trades in a time window: ``GET /trades/historical``.

        Keyset-paged: pass the previous page's ``meta.next_offset`` back for the next.

        :param query_type: Whether the window applies to settlement or event start time.
        :param from_: Window start.
        :param to: Window end.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param market_id: Restrict to one market.
        :param offset: Cursor from the previous page's ``meta.next_offset``.
        :param secondary_offset: Cursor from the previous page's ``meta.next_offset``.
        :param limit: Rows per page.
        :param sort: ``"ASC"`` or ``"DESC"``.
        :returns: One page of settled trades.
        """
        return self.conn.call(
            OffsetPageTradeHistoricalResponse, "GET", "/trades/historical", params={
                "walletId": self.conn.resolve_wallet_id(wallet_id),
                "queryType": query_type,
                "from": from_,
                "to": to,
                "marketId": market_id,
                "offset": offset,
                "secondaryOffset": secondary_offset,
                "limit": limit,
                "sort": sort,
            })
