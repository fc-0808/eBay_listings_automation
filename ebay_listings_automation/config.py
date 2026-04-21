from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_ENV = (os.environ.get("EBAY_ENV") or "sandbox").strip().lower()
if _ENV not in ("sandbox", "production"):
    raise ValueError("EBAY_ENV must be 'sandbox' or 'production'")

SANDBOX = _ENV == "sandbox"

CLIENT_ID = os.environ.get("EBAY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET", "").strip()

# eBay OAuth: the authorize + token requests use redirect_uri=<RuName>, not your callback URL.
# See https://developer.ebay.com/api-docs/static/oauth-redirect-uri.html
RU_NAME = (os.environ.get("EBAY_RU_NAME") or "").strip()
_legacy_redirect = (os.environ.get("EBAY_REDIRECT_URI") or "").strip()
if not RU_NAME and _legacy_redirect and not _legacy_redirect.startswith(("http://", "https://")):
    RU_NAME = _legacy_redirect

# Browser redirect after consent — must match "Auth Accepted URL" for that RuName in the portal.
# eBay requires https for accept/decline URLs (see README); default is HTTPS localhost.
_default_callback = "https://127.0.0.1:8765/oauth/callback"
OAUTH_CALLBACK_URL = (os.environ.get("EBAY_OAUTH_CALLBACK_URL") or "").strip()
if not OAUTH_CALLBACK_URL:
    if _legacy_redirect.startswith(("http://", "https://")):
        OAUTH_CALLBACK_URL = _legacy_redirect
    else:
        OAUTH_CALLBACK_URL = _default_callback

# Optional: where the local socket binds (scheme/host/port/path). Use with a tunnel: public
# https URL in OAUTH_CALLBACK_URL, listen URL stays http://127.0.0.1:PORT/... .
_listen = (os.environ.get("EBAY_OAUTH_LISTEN_URL") or "").strip()
if _listen:
    OAUTH_LISTEN_URL = _listen
else:
    OAUTH_LISTEN_URL = OAUTH_CALLBACK_URL

_root = Path(__file__).resolve().parents[1]


def _repo_path(p: str) -> str:
    if not p:
        return p
    x = Path(p)
    if x.is_absolute():
        return str(x)
    return str((_root / x).resolve())


# Required when OAUTH_LISTEN_URL uses https:// — PEM paths from mkcert (or your own cert).
OAUTH_SSL_CERTFILE = _repo_path((os.environ.get("EBAY_OAUTH_SSL_CERTFILE") or "").strip())
OAUTH_SSL_KEYFILE = _repo_path((os.environ.get("EBAY_OAUTH_SSL_KEYFILE") or "").strip())

TOKEN_PATH = Path(os.environ.get("EBAY_TOKEN_PATH") or _root / ".ebay_tokens.json")
if not TOKEN_PATH.is_absolute():
    TOKEN_PATH = (_root / TOKEN_PATH).resolve()

AUTH_BASE = "https://auth.sandbox.ebay.com" if SANDBOX else "https://auth.ebay.com"
API_BASE = "https://api.sandbox.ebay.com" if SANDBOX else "https://api.ebay.com"
TOKEN_URL = f"{API_BASE}/identity/v1/oauth2/token"

DEFAULT_SCOPES = (
    "https://api.ebay.com/oauth/api_scope/sell.inventory "
    "https://api.ebay.com/oauth/api_scope/sell.account"
).strip()


def require_oauth_credentials() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET in .env (see .env.example)."
        )
    if not RU_NAME:
        raise RuntimeError(
            "Set EBAY_RU_NAME in .env to your Sandbox RuName string from the developer portal "
            "(User Tokens → your app → RuName). It is NOT the http://127.0.0.1 URL — that URL "
            "goes in the portal as Auth Accepted URL. See README."
        )
