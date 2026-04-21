"""
One-shot OAuth login: opens browser (or prints URL), receives redirect, saves tokens.

Prerequisites:
  - Copy .env.example to .env: client id/secret, EBAY_RU_NAME (RuName string from portal), and
    EBAY_OAUTH_CALLBACK_URL (must match Auth Accepted URL in that RuName's config).
"""
from __future__ import annotations

import ssl
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from ebay_listings_automation import config
from ebay_listings_automation import oauth
from ebay_listings_automation import tokens as tokens_mod


def _parse_redirect(callback_url: str) -> tuple[str, int, str]:
    u = urlparse(callback_url)
    if u.scheme not in ("http", "https"):
        raise ValueError("EBAY_OAUTH_CALLBACK_URL must be http or https")
    host = u.hostname or "127.0.0.1"
    port = u.port or (443 if u.scheme == "https" else 80)
    path = u.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return host, port, path


def main() -> None:
    config.require_oauth_credentials()
    listen = config.OAUTH_LISTEN_URL
    public = config.OAUTH_CALLBACK_URL
    if urlparse(public).hostname not in (None, "127.0.0.1", "localhost") and listen == public:
        raise SystemExit(
            "EBAY_OAUTH_CALLBACK_URL points at a non-local host (e.g. ngrok) but "
            "EBAY_OAUTH_LISTEN_URL is not set.\n\n"
            "Set EBAY_OAUTH_LISTEN_URL=http://127.0.0.1:8765/oauth/callback (same path as "
            "your public URL) and run a tunnel (ngrok) to that port."
        )
    host, port, expected_path = _parse_redirect(listen)

    state = oauth.new_oauth_state()
    auth_url = oauth.build_authorize_url(state)
    result: dict[str, str | None] = {"code": None, "error": None, "error_description": None}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != expected_path:
                self.send_error(404, "Path does not match the listen URL path")
                return
            qs = parse_qs(parsed.query)
            if "error" in qs:
                result["error"] = qs["error"][0]
                result["error_description"] = (qs.get("error_description") or [None])[0]
                body = b"OAuth error. You can close this tab."
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)
                event.set()
                return
            if qs.get("state", [None])[0] != state:
                self.send_error(400, "state mismatch")
                event.set()
                return
            code = qs.get("code", [None])[0]
            if not code:
                self.send_error(400, "missing code")
                event.set()
                return
            result["code"] = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"Success. Tokens saved to disk. You can close this browser tab."
            )
            event.set()

    event = threading.Event()
    server = HTTPServer((host, port), Handler)
    listen_parsed = urlparse(listen)
    if listen_parsed.scheme == "https":
        if not config.OAUTH_SSL_CERTFILE or not config.OAUTH_SSL_KEYFILE:
            raise SystemExit(
                "The listen URL is https but EBAY_OAUTH_SSL_CERTFILE / "
                "EBAY_OAUTH_SSL_KEYFILE are not set.\n\n"
                "Either use http://127.0.0.1:… for EBAY_OAUTH_LISTEN_URL with a tunnel, or "
                "create local PEM files with mkcert and point the SSL env vars at them.\n"
                "See README: “Localhost and HTTPS research” and “How others do local OAuth”."
            )
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(config.OAUTH_SSL_CERTFILE, config.OAUTH_SSL_KEYFILE)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("Open this URL in your browser (if it did not open automatically):\n")
    print(auth_url)
    print()
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    wait_url = f"{listen_parsed.scheme}://{host}:{port}{expected_path}"
    print(f"Waiting for browser redirect (eBay → {public}) … local listener: {wait_url}")
    event.wait(timeout=600)
    server.shutdown()
    server.server_close()

    if result["error"]:
        desc = result["error_description"] or ""
        raise SystemExit(f"OAuth failed: {result['error']} {desc}".strip())

    code = result["code"]
    if not code:
        raise SystemExit("Timed out or no authorization code received.")

    token_payload = oauth.exchange_authorization_code(str(code))
    tokens_mod.save_tokens(config.TOKEN_PATH, token_payload)
    print(f"Saved tokens to {config.TOKEN_PATH}")
    print("Next: python smoke_test.py")


if __name__ == "__main__":
    main()
