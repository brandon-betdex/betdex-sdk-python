from betdex.apps.resources import (
    CommissionRateResponse,
    SessionResponse,
)
from betdex.endpoints import Endpoints
from betdex.exceptions import BetDexInvalidRequestError


class AppsEndpoints(Endpoints):
    """
    Sessions, app API keys and commission rates.
    """
    def create_session(
        self,
        app_id: str | None = None,
        api_key: str | None = None,
        wallet_id: str | None = None) -> SessionResponse:
        """
        Log in: ``POST /sessions``.

        Stores the tokens on the connection; refresh before ``access_expires_at``.

        :param app_id: Defaults to the connection's ``app_id``.
        :param api_key: Defaults to the connection's ``api_key``.
        :param wallet_id: Only for ``WALLET`` API keys; not defaulted, as app keys reject it.
        :returns: The new session.
        :raises BetDexInvalidRequestError: If no app id or API key is available.
        """
        body = {
            "appId": app_id or self.conn.app_id,
            "apiKey": api_key or self.conn.api_key,
        }
        if not body["appId"] or not body["apiKey"]:
            raise BetDexInvalidRequestError("app_id and api_key are required to create a session")
        if wallet_id:
            body["walletId"] = wallet_id
        result = self.conn.call(SessionResponse, "POST", "/sessions", json=body)
        if result.sessions:
            self.conn.access_token = result.sessions[0].access_token
            self.conn.refresh_token = result.sessions[0].refresh_token
        return result

    def refresh_session(self, refresh_token: str | None = None) -> SessionResponse:
        """
        Exchange a refresh token for new tokens: ``POST /sessions/refresh``.

        Stores the new tokens on the connection.

        :param refresh_token: Defaults to the connection's ``refresh_token``.
        :returns: The refreshed session.
        :raises BetDexInvalidRequestError: If no refresh token is available.
        """
        token = refresh_token or self.conn.refresh_token
        if not token:
            raise BetDexInvalidRequestError("no refresh token; call create_session first")
        result = self.conn.call(
            SessionResponse, "POST", "/sessions/refresh",
            json={"refreshToken": token})
        if result.sessions:
            self.conn.access_token = result.sessions[0].access_token
            self.conn.refresh_token = result.sessions[0].refresh_token
        return result

    def get_commission_rates(
        self,
        app_id: str | None = None) -> CommissionRateResponse:
        """
        Fetch an app's commission rates: ``GET /apps/{id}/commission-rates``.

        :param app_id: Defaults to the connection's ``app_id``.
        :returns: The app's commission rates.
        :raises BetDexInvalidRequestError: If no app id is available.
        """
        return self.conn.call(
            CommissionRateResponse, "GET", "/apps/{id}/commission-rates",
            path_params={"id": self.conn.resolve_app_id(app_id)})
