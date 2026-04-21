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
REDIRECT_URI = os.environ.get("EBAY_REDIRECT_URI", "").strip()

_root = Path(__file__).resolve().parents[1]
TOKEN_PATH = Path(os.environ.get("EBAY_TOKEN_PATH") or _root / ".ebay_tokens.json")

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
    if not REDIRECT_URI:
        raise RuntimeError(
            "Set EBAY_REDIRECT_URI in .env to match your eBay app RuName exactly."
        )
