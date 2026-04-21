from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def load_tokens(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    return data


def save_tokens(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def access_token_expired(payload: dict[str, Any], skew_seconds: int = 120) -> bool:
    exp = payload.get("obtained_at") and payload.get("expires_in")
    if not exp:
        return True
    obtained = float(payload["obtained_at"])
    ttl = int(payload["expires_in"])
    return time.time() >= obtained + ttl - skew_seconds
