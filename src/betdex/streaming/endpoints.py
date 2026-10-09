from betdex.endpoints import Endpoints
from betdex.streaming.listener import BaseListener, StreamListener
from betdex.streaming.stream import BetDexStream


class StreamingEndpoints(Endpoints):
    """
    The Stream API.
    """

    def create_stream(
        self,
        listener: BaseListener | None = None,
        *,
        url: str | None = None,
        timeout: float = 30.0,
        keepalive: float | None = 60.0,
    ) -> BetDexStream:
        """
        Create a stream on this connection; nothing is sent until it connects.

        :param listener: Receives every frame; a new ``StreamListener`` if omitted.
        :param url: Stream URL; defaults to the connection's ``stream_url``.
        :param timeout: Seconds to wait to connect, or for the authentication reply.
        :param keepalive: Seconds without a frame before sending a ping; ``None`` never pings.
        :returns: The stream.
        """
        return BetDexStream(
            self.conn,
            listener if listener is not None else StreamListener(),
            url=url,
            timeout=timeout,
            keepalive=keepalive,
        )
