from __future__ import annotations

from typing import Any

import httpx

from . import config
from . import oauth
from . import tokens as tokens_mod


class EbaySession:
    """User access token with automatic refresh using stored refresh_token."""

    def __init__(self, token_path: Any | None = None) -> None:
        self._token_path = token_path or config.TOKEN_PATH
        self._payload: dict[str, Any] | None = tokens_mod.load_tokens(self._token_path)

    def _persist(self, payload: dict[str, Any]) -> None:
        tokens_mod.save_tokens(self._token_path, payload)
        self._payload = payload

    def ensure_access_token(self) -> str:
        if self._payload is None:
            raise RuntimeError(
                "No saved tokens. Run: python run_oauth.py"
            )
        rt = self._payload.get("refresh_token")
        at = self._payload.get("access_token")
        if not rt or not at:
            raise RuntimeError("Token file is missing refresh_token or access_token.")

        if not tokens_mod.access_token_expired(self._payload):
            return str(at)

        refreshed = oauth.refresh_access_token(str(rt))
        merged = {**self._payload, **refreshed}
        self._persist(merged)
        return str(merged["access_token"])

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """
        path: e.g. '/sell/inventory/v1/inventory_item?limit=1'
        """
        url = f"{config.API_BASE}{path}" if path.startswith("/") else f"{config.API_BASE}/{path}"
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {self.ensure_access_token()}"
        with httpx.Client(timeout=60.0) as client:
            return client.request(method, url, headers=headers, **kwargs)
