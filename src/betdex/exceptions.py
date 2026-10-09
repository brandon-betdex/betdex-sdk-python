from datetime import datetime

import requests
from typing import Any



class BetDexError(Exception):
    """
    Base class for every error this SDK raises.
    """


class BetDexConfigurationError(BetDexError):
    """
    The connection is set up wrongly, e.g. an unknown environment.
    """


class BetDexInvalidRequestError(BetDexError):
    """
    A call is missing a required value; raised before anything is sent.
    """


class BetDexInvalidPriceError(BetDexError):
    """
    A price is off the price ladder, or a ladder operation would leave it.
    """


class BetDexDecodeError(BetDexError):
    """
    A 2xx response body could not be decoded; the cause is the ``__cause__``.
    """


class BetDexTransportError(BetDexError):
    """
    The request got no response; the ``requests`` error is the ``__cause__``.

    :param message: What failed.
    :param sent_at: When the request was sent (UTC).
    :param latency_ms: Milliseconds from sending until it failed.
    """

    def __init__(self, message: str, *, sent_at: datetime, latency_ms: float) -> None:
        """
        Create the error; see the class docstring for parameters.
        """
        super().__init__(message)
        self.sent_at = sent_at
        self.latency_ms = latency_ms


class BetDexSocketError(BetDexError):
    """
    The stream's socket could not connect, failed, or was closed by the server;
    any underlying error is the ``__cause__``.
    """


class BetDexStreamAuthenticationError(BetDexError):
    """
    The stream did not accept the access token.
    """


class BetDexAPIError(BetDexError):
    """
    The API answered with a non-2xx status.

    :param response: The failed response.
    :param sent_at: When the request was sent (UTC).
    :param received_at: When the response arrived (UTC).
    :param latency_ms: Milliseconds from sending to the response.

    :ivar status_code: HTTP status code, e.g. 404.
    :ivar title: The error body's ``title``, if any.
    :ivar details: The error body's ``details``.
    :ivar body: The decoded JSON body, or the text if not JSON.
    :ivar response: The ``requests.Response``.
    """

    def __init__(
        self,
        response: requests.Response,
        *,
        sent_at: datetime,
        received_at: datetime,
        latency_ms: float,
    ) -> None:
        """
        Create the error from a failed response; see the class docstring for parameters.
        """
        try:
            body: Any = response.json()
        except ValueError:
            body = response.text

        title = None
        details: list[str] = []
        if isinstance(body, dict):
            title = body.get("title")
            raw_details = body.get("details")
            if isinstance(raw_details, list):
                details = [str(d) for d in raw_details]
            elif raw_details is not None:
                details = [str(raw_details)]

        self.status_code = response.status_code
        self.title = title
        self.details = details
        self.body = body
        self.response = response
        self.sent_at = sent_at
        self.received_at = received_at
        self.latency_ms = latency_ms
        summary = title or response.reason or "error"
        if details:
            summary += ": " + "; ".join(details)
        super().__init__(f"{self.status_code} {summary}")
