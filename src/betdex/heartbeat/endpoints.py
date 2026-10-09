from betdex.endpoints import Endpoints
from betdex.heartbeat.resources import HeartbeatResponse


class HeartbeatEndpoints(Endpoints):
    """
    The app's dead-man's switch. Not in the published API spec.
    """

    def get_heartbeat(self) -> HeartbeatResponse:
        """
        Fetch this app's heartbeat: ``GET /heartbeats``.

        :returns: The armed heartbeat.
        :raises BetDexAPIError: 404 if no heartbeat is armed.
        """
        return self.conn.call(HeartbeatResponse, "GET", "/heartbeats")

    def send_heartbeat(self, timeout_ms: int) -> HeartbeatResponse:
        """
        Arm or refresh this app's dead-man's switch: ``POST /heartbeats``.

        If no heartbeat arrives within ``timeout_ms``, the exchange blocks the app's
        new orders and cancels its unmatched ones.

        :param timeout_ms: Window in milliseconds, 10000–300000.
        :returns: The heartbeat after the update.
        """
        return self.conn.call(
            HeartbeatResponse, "POST", "/heartbeats", json={"timeoutMs": timeout_ms})

    def delete_heartbeat(self) -> HeartbeatResponse:
        """
        Disarm this app's dead-man's switch: ``DELETE /heartbeats``.

        Also lifts an order block imposed by a missed heartbeat.

        :returns: The heartbeat as it was before deletion.
        """
        return self.conn.call(HeartbeatResponse, "DELETE", "/heartbeats")
