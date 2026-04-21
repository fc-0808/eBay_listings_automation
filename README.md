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

   - `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` from **Application Keys** (Sandbox first).
   - **`EBAY_RU_NAME`** — the **RuName** string eBay shows after you configure redirects (see below). This is what the OAuth `redirect_uri` parameter must be; it is **not** the `http://127.0.0.1/...` URL.
   - **`EBAY_OAUTH_CALLBACK_URL`** — usually `http://127.0.0.1:8765/oauth/callback`. It must match **Auth Accepted URL** in the portal for that RuName **exactly**.
   - `EBAY_ENV=sandbox` until you use Production keys.

### Where to add `http://127.0.0.1:8765/oauth/callback` (RuName setup)

eBay splits this into two ideas ([official doc](https://developer.ebay.com/api-docs/static/oauth-redirect-uri.html)):

| In the **developer portal** | In **`.env`** |
|------------------------------|---------------|
| **Auth Accepted URL** = `http://127.0.0.1:8765/oauth/callback` | `EBAY_OAUTH_CALLBACK_URL` = the same URL |
| After you save, eBay shows a **RuName** (a short identifier like `YourApp-SBX-…`) | `EBAY_RU_NAME` = that RuName string |

**Clicks in the portal:**

1. Sign in at [developer.ebay.com](https://developer.ebay.com).
2. **Your account** (top right) → **Application Keys** (or **Application Keysets**).
3. Under **Sandbox**, find your app (**Listings automation**).
4. Click **User Tokens** — the link **right next to your Sandbox App ID** (not only the profile menu).
5. Open **Get a Token from eBay via Your Application** (dropdown/section).
6. If you have no redirect yet: **You have no Redirect URLs. Click here to add one** (or **+ Add eBay Redirect URL**). Confirm legal address if asked.
7. Fill the form, for example:
   - **Display Title**: anything (e.g. `Local dev`).
   - **Privacy Policy URL**: any HTTPS URL you control that hosts a short policy page (eBay requires a value for user tokens). For quick local testing, use a real page you own; placeholder domains often fail validation.
   - **Auth Accepted URL**: `http://127.0.0.1:8765/oauth/callback`
   - **Auth Declined URL**: same as accepted, or another page you control.
   - Enable **OAuth** for this redirect row, then **Save**.
8. Copy the **Sandbox RuName** value eBay displays and paste it into `.env` as **`EBAY_RU_NAME`**.

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

- [Getting your redirect_uri value (RuName vs URLs)](https://developer.ebay.com/api-docs/static/oauth-redirect-uri.html)
- [OAuth authorization code grant (eBay)](https://developer.ebay.com/api-docs/static/oauth-auth-code-grant-request.html)
- [Getting user consent](https://developer.ebay.com/api-docs/static/oauth-consent-request.html)
