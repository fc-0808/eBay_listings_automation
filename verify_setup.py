"""
Sanity-check .env, RuName, and mkcert PEMs before run_oauth.py.
Does not call eBay APIs or open a browser.
"""
from __future__ import annotations

import ssl
import sys
from pathlib import Path
from urllib.parse import urlparse

# Ensure project root is on path when run as `python verify_setup.py`
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    try:
        from ebay_listings_automation import config
    except Exception as e:
        print(f"FAIL: cannot import config ({e}). Run from project root, pip install -r requirements.txt")
        return 1

    issues: list[str] = []
    if not config.CLIENT_ID:
        issues.append("EBAY_CLIENT_ID is empty")
    if not config.CLIENT_SECRET:
        issues.append("EBAY_CLIENT_SECRET is empty")
    if not config.RU_NAME:
        issues.append("EBAY_RU_NAME is empty")
    if not config.OAUTH_CALLBACK_URL:
        issues.append("EBAY_OAUTH_CALLBACK_URL is empty")

    listen = urlparse(config.OAUTH_LISTEN_URL)
    if listen.scheme == "https":
        cert = config.OAUTH_SSL_CERTFILE
        key = config.OAUTH_SSL_KEYFILE
        if not cert or not Path(cert).is_file():
            issues.append(f"HTTPS listen but missing cert file: {cert!r}")
        if not key or not Path(key).is_file():
            issues.append(f"HTTPS listen but missing key file: {key!r}")
        if cert and key and Path(cert).is_file() and Path(key).is_file():
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(cert, key)
            except OSError as e:
                issues.append(f"SSL load_cert_chain failed: {e}")

    public = urlparse(config.OAUTH_CALLBACK_URL)
    if public.scheme != "https":
        issues.append("EBAY_OAUTH_CALLBACK_URL should be https:// for eBay RuName auth URLs")

    if public.hostname not in (None, "127.0.0.1", "localhost") and not config.OAUTH_LISTEN_URL:
        pass  # handled at runtime by run_oauth

    if issues:
        print("Issues:")
        for i in issues:
            print(f"  - {i}")
        return 1

    print("OK - env and TLS materials look usable.")
    print(f"  EBAY_ENV={config.SANDBOX and 'sandbox' or 'production'}")
    print(f"  EBAY_RU_NAME set: yes ({len(config.RU_NAME)} chars)")
    print(f"  EBAY_OAUTH_CALLBACK_URL={config.OAUTH_CALLBACK_URL}")
    if listen.scheme == "https":
        print(f"  SSL cert/key load: OK ({config.OAUTH_SSL_CERTFILE})")
    tok = config.TOKEN_PATH
    if tok.is_file():
        print(f"  Token file exists: {tok} (run smoke_test.py)")
    else:
        print(f"  Token file missing: {tok} - next: python run_oauth.py")
    print("\nIf the browser warns about the certificate, run **mkcert -install** once in an elevated terminal")
    print("so the local CA is trusted (Windows: Admin PowerShell).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
