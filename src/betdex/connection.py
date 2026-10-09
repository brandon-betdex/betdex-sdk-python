import time
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import requests

from betdex.exceptions import (
    BetDexAPIError,
    BetDexConfigurationError,
    BetDexDecodeError,
    BetDexInvalidRequestError,
    BetDexTransportError,
)
from betdex.utils import MAX_PAGE_SIZE, decode, format_query_params

__all__ = ["ENVIRONMENTS", "MAX_PAGE_SIZE", "STREAM_ENVIRONMENTS", "BetDexConnection"]

ENVIRONMENTS: dict[str, str] = {
    "prod": "https://prod.api.btdx.io",
    "sandbox": "https://sandbox.api.btdx.io",
}

STREAM_ENVIRONMENTS: dict[str, str] = {
    "prod": "wss://prod.stream.btdx.io",
    "sandbox": "wss://sandbox.stream.btdx.io",
}


class BetDexConnection:
    """
    Where and how to reach the BetDEX API.

    Every endpoint function takes one first::

        conn = Connection(app_id, api_key, wallet_id, environment="prod")
        apps.create_session(conn)
        markets.get_markets(conn, event_ids=["123"])

    :param app_id: Used by ``create_session`` and as the default for app-scoped calls.
    :param api_key: API key secret, used by ``create_session``.
    :param wallet_id: Default for wallet-scoped calls.
    :param environment: ``"prod"`` or ``"sandbox"``; ignored for a URL that is given.
    :param base_url: API root, overriding ``environment``.
    :param stream_url: Stream API URL, overriding ``environment``.
    :param session: ``requests.Session`` to send through; created if omitted.
    :param timeout: Seconds to wait per request; ``None`` waits forever.
    """

    def __init__(
        self,
        app_id: str | None = None,
        api_key: str | None = None,
        wallet_id: str | None = None,
        *,
        environment: str = "sandbox",
        base_url: str | None = None,
        stream_url: str | None = None,
        session: requests.Session | None = None,
        timeout: float | None = 30.0,
    ) -> None:
        """
        Create a connection; see the class docstring for parameters.

        :raises BetDexConfigurationError: If ``environment`` is unknown and a URL is not given.
        """
        if (base_url is None or stream_url is None) and environment not in ENVIRONMENTS:
            raise BetDexConfigurationError(
                f"unknown environment {environment!r}; "
                f"expected one of {sorted(ENVIRONMENTS)} or a base_url and stream_url")
        base_url = base_url or ENVIRONMENTS[environment]
        stream_url = stream_url or STREAM_ENVIRONMENTS[environment]

        self.app_id = app_id
        self.api_key = api_key
        self.wallet_id = wallet_id
        self.base_url = base_url.rstrip("/")
        self.stream_url = stream_url
        self.http = session or requests.Session()
        self.timeout = timeout

        # Bearer tokens. Set by ``create_session`` and ``refresh_session``; may
        # also be assigned directly to reuse a session obtained elsewhere.
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """
        Send a request to any path, e.g. one this SDK does not cover yet.

        :param method: HTTP method.
        :param path: Path below ``base_url``, e.g. ``"/orders"``.
        :param params: Query parameters; ``None`` dropped, lists comma-joined (``sort``
            repeated), datetimes as UTC ISO 8601, booleans lower-case.
        :param json: Request body.
        :returns: The decoded JSON body, or ``None`` if empty.
        :raises BetDexAPIError: On a non-2xx response.
        :raises BetDexTransportError: If no response was received.
        :raises BetDexDecodeError: If a 2xx body is not JSON.
        """
        return self._send(method, path, params, json)[0]

    def call(
        self,
        model: Any,
        method: str,
        path: str,
        *,
        path_params: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """
        Send a request and decode the body into ``model``, stamped with its timings.

        :param model: Response model to decode into.
        :param method: HTTP method.
        :param path: Path below ``base_url``, with ``{placeholders}``.
        :param path_params: Placeholder values; URL-escaped.
        :param params: Query parameters, encoded as in ``request``.
        :param json: Request body.
        :returns: The decoded model.
        :raises BetDexInvalidRequestError: If a path parameter is empty.
        :raises BetDexDecodeError: If the body does not fit ``model``.
        """
        if path_params:
            missing = [k for k, v in path_params.items() if not v]
            if missing:
                raise BetDexInvalidRequestError(f"{path} needs a value for {', '.join(missing)}")
            path = path.format_map(
                {k: quote(str(v), safe="") for k, v in path_params.items()})
        body, sent_at, received_at, latency_ms = self._send(method, path, params, json)
        try:
            result = decode(model, body or {})
        except BetDexDecodeError as exc:
            raise BetDexDecodeError(f"{method} {path}: body does not fit {model.__name__}") from exc
        result.sent_at = sent_at
        result.received_at = received_at
        result.latency_ms = latency_ms
        return result

    def _send(
        self,
        method: str,
        path: str,
        params: Mapping[str, Any] | None,
        json: Any,
    ) -> tuple[Any, datetime, datetime, float]:
        """
        Send a request, timing it.

        :returns: The decoded JSON body (or ``None`` if empty), when it was sent and
            when the response arrived (UTC), and the round trip in milliseconds.
        """
        headers = {"Accept": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        sent_at = datetime.now(timezone.utc)
        started = time.perf_counter()
        try:
            response = self.http.request(
                method,
                self.base_url + path,
                params=format_query_params(params or {}),
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise BetDexTransportError(
                f"{method} {path} failed: {exc}", sent_at=sent_at,
                latency_ms=(time.perf_counter() - started) * 1000) from exc
        # The monotonic clock times the trip; the wall clock can jump.
        latency_ms = (time.perf_counter() - started) * 1000
        received_at = datetime.now(timezone.utc)
        if not response.ok:
            raise BetDexAPIError(
                response, sent_at=sent_at, received_at=received_at, latency_ms=latency_ms)
        if not response.content:
            return None, sent_at, received_at, latency_ms
        try:
            return response.json(), sent_at, received_at, latency_ms
        except ValueError as exc:
            raise BetDexDecodeError(f"{method} {path} returned a non-JSON body") from exc

    def resolve_wallet_id(self, wallet_id: str | None) -> str:
        """
        Resolve a wallet id argument, falling back to the connection's default.

        :param wallet_id: Explicit wallet id, or ``None``.
        :returns: The wallet id to use.
        :raises BetDexInvalidRequestError: If neither is set.
        """
        resolved = wallet_id or self.wallet_id
        if not resolved:
            raise BetDexInvalidRequestError("wallet_id is required (no default wallet_id set)")
        return resolved

    def resolve_app_id(self, app_id: str | None) -> str:
        """
        Resolve an app id argument, falling back to the connection's default.

        :param app_id: Explicit app id, or ``None``.
        :returns: The app id to use.
        :raises BetDexInvalidRequestError: If neither is set.
        """
        resolved = app_id or self.app_id
        if not resolved:
            raise BetDexInvalidRequestError("app_id is required (no default app_id set)")
        return resolved
