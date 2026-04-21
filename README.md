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
   - **`EBAY_OAUTH_CALLBACK_URL`** — must match **Auth Accepted URL** in the portal **exactly** (see [Localhost and HTTPS](#localhost-and-https-research) — use **HTTPS**).
   - **`EBAY_OAUTH_LISTEN_URL`** — optional; defaults to **`EBAY_OAUTH_CALLBACK_URL`**. Only needed for a **tunnel** (e.g. ngrok): public `https://…` in **`EBAY_OAUTH_CALLBACK_URL`**, local `http://127.0.0.1:…` here (see [Optional tunnel](#optional-ngrok-or-other-tunnel)).
   - **`EBAY_OAUTH_SSL_CERTFILE`** / **`EBAY_OAUTH_SSL_KEYFILE`** — required for the **default** flow: **HTTPS on your own machine** (e.g. **mkcert**). Omit them only when using a tunnel that terminates TLS before your listener.
   - `EBAY_ENV=sandbox` until you use Production keys.

**mkcert + verify:** In the project directory, run **`mkcert -install`** once (use **Administrator** PowerShell on Windows so the OS trusts `https://127.0.0.1`), then **`mkcert 127.0.0.1`**. Add the two PEM paths to **`EBAY_OAUTH_SSL_CERTFILE`** and **`EBAY_OAUTH_SSL_KEYFILE`** in `.env`. Run **`python verify_setup.py`** — it should print `OK` if credentials and TLS files load. The PEMs are listed in `.gitignore`.

### Localhost and HTTPS research

**For the RuName “Auth accepted / declined” fields in the developer portal: effectively no — eBay expects HTTPS.**

Sources:

1. **eBay Developer Support** (forum, 2024): Auth Accepted URL “must support SSL and must use the **HTTPS** protocol,” or you rely on eBay’s default accept page if your app cannot host HTTPS. ([community thread](https://community.ebay.com/t5/eBay-APIs-Talk-to-your-fellow/Test-oAuth-over-localhost-redirect-url/td-p/34712126))
2. **eBay KB** (updated 2022): “Is HTTPS required for Accept and Reject URLs? **Yes**, both the accept and reject urls are required to be https. This is true both for the **sandbox** and for **production**.” ([KB article](https://developer.ebay.com/support/kb-article?KBid=109))
3. **Developers report** the Save action staying disabled or validation failing when using `http://` or even `https://localhost…` in some cases; one workaround discussed is leaving eBay’s default redirect and **manually** copying the `?code=…` query string to a local URL (fragile, only for quick hacking). ([same thread](https://community.ebay.com/t5/eBay-APIs-Talk-to-your-fellow/Test-oAuth-over-localhost-redirect-url/td-p/34712126))

So: use a **real `https://` callback** in the RuName form. Most developers do **not** use ngrok for that unless they have a specific reason.

### How others do local OAuth (without ngrok)

What shows up repeatedly in **community write-ups and open-source tools**:

1. **[gangyistudios/ebay-oauth-cli](https://github.com/gangyistudios/ebay-oauth-cli)** (Node, widely linked): map **`127.0.0.1 local.host`** in the OS **hosts** file (because some validators dislike **`localhost`**), generate **self-signed PEMs** with **OpenSSL**, run a small **HTTPS** server locally, and (if needed) relax Chrome for local dev. Same story in the companion [Medium walkthrough](https://medium.com/@gangyistudios/generate-user-application-access-tokens-for-ebay-restful-apis-locally-from-the-command-line-40fbc66f6397). **No ngrok** — everything stays on the machine.
2. **Forums** ([example thread](https://community.ebay.com/t5/eBay-APIs-Talk-to-your-fellow/Test-oAuth-over-localhost-redirect-url/td-p/34712126)): eBay states **HTTPS** for Auth accepted URLs; workarounds include **eBay’s default accept page** then **manually** copying `?code=…` to a local URL — possible for a one-off, awkward for a repeatable script.
3. **This repo’s default (simplest stable loop):** **[mkcert](https://github.com/FiloSottile/mkcert)** instead of raw OpenSSL: install the local CA once, run `mkcert -install`, then `mkcert 127.0.0.1` (or `mkcert local.host` if you added **`127.0.0.1 local.host`** to hosts and prefer that hostname in the portal). Set **`EBAY_OAUTH_SSL_CERTFILE`** / **`EBAY_OAUTH_SSL_KEYFILE`** to the generated PEMs, set **`EBAY_OAUTH_CALLBACK_URL`** to the same **`https://…`** URL you put in eBay (**Auth accepted / declined**), leave **`EBAY_OAUTH_LISTEN_URL`** unset, run **`python run_oauth.py`**. **No rotating tunnel URL**, no extra vendor account for basic dev.

**GitHub / `github.io`:** still a good place to host a **privacy policy** (`raw.githubusercontent.com` or Pages). It is **not** a substitute for a local HTTPS listener for this Python flow unless you build a separate “paste the code” page yourself.

### Optional: ngrok (or other tunnel)

Use a tunnel **only** if you cannot use mkcert (policy blocks local CA), or you need someone else’s browser to hit your laptop without DNS/hosts tricks. Then: `ngrok http 8765`, set **`EBAY_OAUTH_CALLBACK_URL`** to the **https** forwarding URL (plus path **`/oauth/callback`**), **`EBAY_OAUTH_LISTEN_URL=http://127.0.0.1:8765/oauth/callback`**, leave SSL env vars empty. Remember free ngrok URLs **change** when the process restarts unless you pay for a **reserved domain** — that churn is exactly the “extra confusing step” people want to skip for day-to-day work.

### Copy-paste: eBay Sign-in Settings (Sandbox RuName)

Paste into eBay’s form fields, then **Save**. (We cannot type into eBay for you; this is the exact text to use.)

| eBay field | Paste this |
|------------|------------|
| **Display title** | `Sandbox local — Listings automation` |
| **Your privacy policy URL** | `https://raw.githubusercontent.com/fc-0808/eBay_listings_automation/main/docs/privacy.html` |
| **Your auth accepted URL** | `https://127.0.0.1:8765/oauth/callback` |
| **Your auth declined URL** | `https://127.0.0.1:8765/oauth/callback` |
| **Sign-in method** | **OAuth** (not Auth’n’auth) |

That privacy URL is a minimal policy page in this repo (`docs/privacy.html`) served over **HTTPS** via GitHub’s `raw.githubusercontent.com` CDN. It only works after this file exists on your **`main`** branch (run `git push` if you have not yet).

If eBay’s validator rejects `raw.githubusercontent.com`, use any **https://** page you control instead and keep the two auth URLs identical to the table above.

### RuName setup (portal vs `.env`)

eBay splits this into two ideas ([official doc](https://developer.ebay.com/api-docs/static/oauth-redirect-uri.html)):

| In the **developer portal** | In **`.env`** |
|------------------------------|---------------|
| **Auth Accepted URL** (HTTPS) — same string as your local / tunnel URL | `EBAY_OAUTH_CALLBACK_URL` |
| **RuName** string eBay shows for that row | `EBAY_RU_NAME` (this is the OAuth `redirect_uri` parameter in API calls, not the URL above) |

**Clicks in the portal:**

1. Sign in at [developer.ebay.com](https://developer.ebay.com).
2. **Your account** (top right) → **Application Keys** (or **Application Keysets**).
3. Under **Sandbox**, find your app (**Listings automation**).
4. Click **User Tokens** — the link **right next to your Sandbox App ID** (not only the profile menu).
5. Open **Get a Token from eBay via Your Application** (dropdown/section).
6. If you have no redirect yet: **You have no Redirect URLs. Click here to add one** (or **+ Add eBay Redirect URL**). Confirm legal address if asked.
7. Fill the form using the **Copy-paste** table above, then **Save**.
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

- [Is HTTPS required for Accept and Reject URLs? (KB)](https://developer.ebay.com/support/kb-article?KBid=109)
- [Test OAuth over localhost / Auth Accepted URL (community)](https://community.ebay.com/t5/eBay-APIs-Talk-to-your-fellow/Test-oAuth-over-localhost-redirect-url/td-p/34712126)
- [Getting your redirect_uri value (RuName vs URLs)](https://developer.ebay.com/api-docs/static/oauth-redirect-uri.html)
- [OAuth authorization code grant (eBay)](https://developer.ebay.com/api-docs/static/oauth-auth-code-grant-request.html)
- [Getting user consent](https://developer.ebay.com/api-docs/static/oauth-consent-request.html)
- [gangyistudios/ebay-oauth-cli](https://github.com/gangyistudios/ebay-oauth-cli) (community: hosts + local HTTPS, no tunnel)
