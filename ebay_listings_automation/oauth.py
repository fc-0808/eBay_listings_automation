from __future__ import annotations

import base64
import secrets
import time
import urllib.parse
from typing import Any

import httpx

from . import config


def _basic_auth_header() -> str:
    raw = f"{config.CLIENT_ID}:{config.CLIENT_SECRET}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def build_authorize_url(state: str, scopes: str | None = None) -> str:
    config.require_oauth_credentials()
    scope = scopes or config.DEFAULT_SCOPES
    q = urllib.parse.urlencode(
        {
            "client_id": config.CLIENT_ID,
            "redirect_uri": config.REDIRECT_URI,
            "response_type": "code",
            "scope": scope,
            "state": state,
        }
    )
    return f"{config.AUTH_BASE}/oauth2/authorize?{q}"


def exchange_authorization_code(code: str) -> dict[str, Any]:
    config.require_oauth_credentials()
    body = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.REDIRECT_URI,
        }
    )
    r = httpx.post(
        config.TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": _basic_auth_header(),
        },
        content=body,
        timeout=60.0,
    )
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected token response")
    data["obtained_at"] = time.time()
    return data


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    config.require_oauth_credentials()
    body = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": refresh_token}
    )
    r = httpx.post(
        config.TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": _basic_auth_header(),
        },
        content=body,
        timeout=60.0,
    )
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected token response")
    data["obtained_at"] = time.time()
    # eBay may omit refresh_token on refresh; keep the old one
    if "refresh_token" not in data or data["refresh_token"] in (None, "N/A"):
        data["refresh_token"] = refresh_token
    return data


def new_oauth_state() -> str:
    return secrets.token_urlsafe(32)
