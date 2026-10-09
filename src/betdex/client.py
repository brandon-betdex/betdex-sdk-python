import requests

from betdex.apps import AppsEndpoints
from betdex.connection import BetDexConnection
from betdex.events import EventsEndpoints
from betdex.heartbeat import HeartbeatEndpoints
from betdex.markets import MarketsEndpoints
from betdex.orders import OrdersEndpoints
from betdex.streaming import StreamingEndpoints
from betdex.wallets import WalletsEndpoints


class BetDexClient(
    AppsEndpoints,
    HeartbeatEndpoints,
    EventsEndpoints,
    MarketsEndpoints,
    OrdersEndpoints,
    WalletsEndpoints,
    StreamingEndpoints,
):
    """
    Top-level client for betdex.
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
        Create the client and its connection; see ``Connection`` for parameters.
        """
        super().__init__(BetDexConnection(
            app_id,
            api_key,
            wallet_id,
            environment=environment,
            base_url=base_url,
            stream_url=stream_url,
            session=session,
            timeout=timeout,
        ))
