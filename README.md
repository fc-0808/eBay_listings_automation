# eBay listings automation

Python toolkit to connect your eBay developer app to the **Sell Inventory** REST APIs: OAuth 2.0 (authorization code grant), token refresh on disk, and a small smoke test.

## Why GitHub looked empty

The remote at [fc-0808/eBay_listings_automation](https://github.com/fc-0808/eBay_listings_automation) only shows code **after** a successful `git push` from a folder that contains commits. This project was initialized here with real files and git history so you can push from the folder below.

## Setup

1. **Python 3.10+** recommended.

2. Create a virtual environment and install dependencies:

   ```text
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set:

   - `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` from the eBay Developers **Application Keys** page (start with **Sandbox**).
   - `EBAY_REDIRECT_URI` — must match the **OAuth redirect (RuName)** configured for that app **exactly** (scheme, host, port, path).
   - `EBAY_ENV=sandbox` until you are ready for production keys and endpoints.

4. **Run OAuth once** (starts a tiny local server and opens the consent URL):

   ```text
   python run_oauth.py
   ```

5. **Verify an API call**:

   ```text
   python smoke_test.py
   ```

You should see `HTTP 200` and a short success line. If you get `401` or `403`, regenerate the user token with the scopes in `ebay_listings_automation/config.py` (`sell.inventory`, `sell.account`).

## Security

- Never commit `.env` or `.ebay_tokens.json` (both are gitignored).
- If secrets were ever pasted into a ticket or screenshot, **rotate** the Cert ID in the developer portal.

## Push this repo to GitHub

From this directory (where `.git` will live):

```text
git init
git add .
git commit -m "Initial eBay OAuth and inventory smoke test"
git branch -M main
git remote add origin https://github.com/fc-0808/eBay_listings_automation.git
git push -u origin main
```

If `git push` asks for credentials, use a [Personal Access Token](https://github.com/settings/tokens) as the password (HTTPS), or switch the remote to SSH.

## References

- [OAuth authorization code grant (eBay)](https://developer.ebay.com/api-docs/static/oauth-auth-code-grant-request.html)
- [Getting user consent](https://developer.ebay.com/api-docs/static/oauth-consent-request.html)
