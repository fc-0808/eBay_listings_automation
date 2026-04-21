"""Call Sell Inventory API with your saved user token (proves OAuth + refresh work)."""
from __future__ import annotations

import json
import sys

from ebay_listings_automation import config
from ebay_listings_automation.client import EbaySession


def main() -> None:
    session = EbaySession()
    r = session.request("GET", "/sell/inventory/v1/inventory_item", params={"limit": 5})
    print(f"HTTP {r.status_code}")
    try:
        data = r.json()
    except Exception:
        print(r.text[:2000])
        sys.exit(1)
    if r.status_code >= 400:
        print(json.dumps(data, indent=2))
        sys.exit(1)
    total = data.get("total", data.get("href", ""))
    print("OK — authenticated call succeeded.")
    print(f"Response snippet: total={total!r}, keys={list(data.keys())}")


if __name__ == "__main__":
    main()
