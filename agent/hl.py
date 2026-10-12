"""Hyperliquid public data, used read-only as a positioning signal (no trading here)."""
import time

import httpx

from . import config

_http = httpx.Client(timeout=20)


def info(body, tries=5):
    for i in range(tries):
        r = _http.post(f"{config.HL_API}/info", json=body)
        if r.status_code == 429:
            time.sleep(2 * (i + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Hyperliquid rate limit")


def positioning(coin):
    """Perp funding (hourly), annualized funding, open interest, mark vs oracle premium."""
    meta, ctxs = info({"type": "metaAndAssetCtxs"})
    for a, c in zip(meta["universe"], ctxs):
        if a["name"] == coin:
            f = float(c["funding"])
            return {"coin": coin, "funding_hourly": f, "funding_annualized": round(f * 24 * 365, 4),
                    "open_interest_usd": round(float(c["openInterest"]) * float(c["markPx"])),
                    "premium": float(c.get("premium") or 0), "perp_24h_volume": float(c["dayNtlVlm"])}
    return {"coin": coin, "error": "not listed on Hyperliquid"}


def positions(user):
    s = info({"type": "clearinghouseState", "user": user})
    out = []
    for p in s.get("assetPositions", []):
        p = p["position"]
        out.append({"coin": p["coin"], "size": float(p["szi"]), "entry": float(p["entryPx"] or 0),
                    "notional": float(p["positionValue"]), "upnl": float(p["unrealizedPnl"])})
    return {"account_value": float(s["marginSummary"]["accountValue"]), "positions": out}
