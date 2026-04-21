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
    host, port, expected_path = _parse_redirect(config.OAUTH_CALLBACK_URL)

    state = oauth.new_oauth_state()
    auth_url = oauth.build_authorize_url(state)
    result: dict[str, str | None] = {"code": None, "error": None, "error_description": None}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != expected_path:
                self.send_error(404, "Path does not match EBAY_OAUTH_CALLBACK_URL")
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
    callback = urlparse(config.OAUTH_CALLBACK_URL)
    if callback.scheme == "https":
        if not config.OAUTH_SSL_CERTFILE or not config.OAUTH_SSL_KEYFILE:
            raise SystemExit(
                "EBAY_OAUTH_CALLBACK_URL is https but EBAY_OAUTH_SSL_CERTFILE / "
                "EBAY_OAUTH_SSL_KEYFILE are not set.\n\n"
                "eBay’s portal requires HTTPS for Auth Accepted / Declined URLs. "
                "Create local PEM files, for example with mkcert:\n"
                "  mkcert -install\n"
                "  mkcert 127.0.0.1\n"
                "Then set the two env vars to the generated PEM paths (see .env.example).\n"
                "See README: “Does a local callback URL work?”"
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

    wait_url = f"{callback.scheme}://{host}:{port}{expected_path}"
    print(f"Waiting for redirect on {wait_url} ...")
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
