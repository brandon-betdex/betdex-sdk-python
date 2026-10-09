from collections.abc import Sequence
from datetime import datetime

from betdex.endpoints import Endpoints
from betdex.markets.resources import PagedMarketPositionResponse
from betdex.resources import PositionFilter, Sort
from betdex.wallets.resources import (
    PagedTransactionResponse,
    PagedWalletResponse,
    TransferResponse,
    WalletMetricsResponse,
    WalletResponse,
    WalletType,
)


class WalletsEndpoints(Endpoints):
    """
    Wallets, transactions, positions, metrics, funds and wallet API keys.
    """

    def get_wallets(
        self,
        *,
        wallet_ids: Sequence[str] | None = None,
        types: Sequence[WalletType] | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedWalletResponse:
        """
        Fetch the wallets visible to this session: ``GET /wallets``.

        :param wallet_ids: Wallet ids to match.
        :param types: Wallet types to match.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: A page of wallets.
        """
        return self.conn.call(PagedWalletResponse, "GET", "/wallets", params={
            "walletIds": wallet_ids,
            "types": types,
            "page": page,
            "size": size,
            "sort": sort,
        })

    def get_wallet(self, wallet_id: str | None = None) -> WalletResponse:
        """
        Fetch a wallet and its balances: ``GET /wallets/{id}``.

        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :returns: The wallet.
        """
        return self.conn.call(
            WalletResponse, "GET", "/wallets/{id}",
            path_params={"id": self.conn.resolve_wallet_id(wallet_id)})

    def create_wallet(
        self, *, reference: str | None = None, description: str | None = None,
    ) -> WalletResponse:
        """
        Create a wallet: ``POST /wallets``.

        :param reference: Client-chosen reference.
        :param description: Free-text description.
        :returns: The new wallet.
        """
        body = {"reference": reference, "description": description}
        return self.conn.call(
            WalletResponse, "POST", "/wallets",
            json={k: v for k, v in body.items() if v is not None})

    def get_wallet_transactions(
        self,
        wallet_id: str | None = None,
        *,
        from_created_at: datetime | None = None,
        to_created_at: datetime | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedTransactionResponse:
        """
        Fetch a wallet's ledger: ``GET /wallets/{id}/transactions``.

        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param from_created_at: Earliest creation time.
        :param to_created_at: Latest creation time.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: A page of transactions.
        """
        return self.conn.call(
            PagedTransactionResponse, "GET", "/wallets/{id}/transactions",
            path_params={"id": self.conn.resolve_wallet_id(wallet_id)},
            params={
                "fromCreatedAt": from_created_at,
                "toCreatedAt": to_created_at,
                "page": page,
                "size": size,
                "sort": sort,
            })

    def get_wallet_positions(
        self,
        market_ids: Sequence[str],
        wallet_id: str | None = None,
        *,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedMarketPositionResponse:
        """
        Fetch a wallet's positions on given markets: ``GET /wallets/{id}/positions``.

        Paged (25 rows by default) although the spec doesn't say so. The API rejects
        URLs much over ~7,000 characters, so split very long id lists.

        :param market_ids: Market ids to match.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: One page of positions.
        """
        return self.conn.call(
            PagedMarketPositionResponse, "GET", "/wallets/{id}/positions",
            path_params={"id": self.conn.resolve_wallet_id(wallet_id)},
            params={"marketIds": market_ids, "page": page, "size": size, "sort": sort})

    def get_all_wallet_positions(
        self,
        wallet_id: str | None = None,
        *,
        filter: PositionFilter | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: Sort | None = None,
    ) -> PagedMarketPositionResponse:
        """
        Fetch all of a wallet's positions: ``GET /wallets/{id}/positions-all``.

        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :param filter: ``"Active"`` or ``"Settled"`` markets only.
        :param page: Zero-based page number.
        :param size: Page size, at most ``MAX_PAGE_SIZE``.
        :param sort: Sort keys, e.g. ``["createdAt,desc"]``.
        :returns: A page of positions.
        """
        return self.conn.call(
            PagedMarketPositionResponse, "GET", "/wallets/{id}/positions-all",
            path_params={"id": self.conn.resolve_wallet_id(wallet_id)},
            params={"filter": filter, "page": page, "size": size, "sort": sort})

    def get_wallet_metrics(
        self,
        currency_id: str,
        from_date_time: datetime,
        to_date_time: datetime,
        wallet_id: str | None = None,
    ) -> WalletMetricsResponse:
        """
        Fetch a wallet's order totals by state: ``GET /wallets/{id}/metrics``.

        :param currency_id: Currency to report in.
        :param from_date_time: Start of the window.
        :param to_date_time: End of the window.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :returns: The metrics.
        """
        return self.conn.call(
            WalletMetricsResponse, "GET", "/wallets/{id}/metrics",
            path_params={"id": self.conn.resolve_wallet_id(wallet_id)},
            params={
                "currencyId": currency_id,
                "fromDateTime": from_date_time,
                "toDateTime": to_date_time,
            })

    def credit_wallet(
        self, currency_id: str, wallet_id: str | None = None,
    ) -> TransferResponse:
        """
        Credit a wallet with test funds (sandbox only): ``GET /faucet``.

        :param currency_id: Currency to credit.
        :param wallet_id: Defaults to the connection's ``wallet_id``.
        :returns: The transfer and the credited wallet.
        """
        return self.conn.call(TransferResponse, "GET", "/faucet", params={
            "walletId": self.conn.resolve_wallet_id(wallet_id),
            "currencyId": currency_id,
        })



