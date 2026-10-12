"""Coinbase Advanced Trade public market data (no key needed)."""
import time

import httpx

from . import config

_http = httpx.Client(timeout=20)


def _get(path, params=None, tries=5):
    for i in range(tries):
        r = _http.get(f"{config.CB_API}{path}", params=params)
        if r.status_code == 429:
            time.sleep(1.5 * (i + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Coinbase rate limit")


def snapshot(pid):
    p = _get(f"/market/products/{pid}")
    return {"product": pid, "price": float(p["price"]),
            "chg_24h_pct": float(p.get("price_percentage_change_24h") or 0),
            "volume_24h": float(p.get("volume_24h") or 0),
            "base_increment": p["base_increment"], "quote_increment": p["quote_increment"]}


def book(pid, limit=50):
    b = _get("/market/product_book", {"product_id": pid, "limit": limit})["pricebook"]
    bids = [(float(x["price"]), float(x["size"])) for x in b["bids"]]
    asks = [(float(x["price"]), float(x["size"])) for x in b["asks"]]
    return bids, asks


GRAN = {"5m": ("FIVE_MINUTE", 300), "15m": ("FIFTEEN_MINUTE", 900), "1h": ("ONE_HOUR", 3600),
        "6h": ("SIX_HOUR", 21600), "1d": ("ONE_DAY", 86400)}


def candles(pid, interval="1h", hours=72):
    g, secs = GRAN[interval]
    end = int(time.time())
    start = max(end - hours * 3600, end - 340 * secs)
    c = _get(f"/market/products/{pid}/candles", {"start": start, "end": end, "granularity": g})["candles"]
    rows = [(int(x["start"]), float(x["open"]), float(x["high"]), float(x["low"]), float(x["close"]), float(x["volume"]))
            for x in c]
    return sorted(rows)


def realized_vol(pid, interval="1d", hours=24 * 60):
    cs = candles(pid, interval, hours)
    r = [cs[i][4] / cs[i - 1][4] - 1 for i in range(1, len(cs))]
    if len(r) < 2:
        return None
    m = sum(r) / len(r)
    return (sum((x - m) ** 2 for x in r) / (len(r) - 1)) ** 0.5


def walk(levels, quote_amount=None, base_amount=None):
    """Average fill for a taker order sized in quote (buy) or base (sell)."""
    got = cost = 0.0
    for px, sz in levels:
        if quote_amount is not None:
            take = min(sz, (quote_amount - cost) / px)
        else:
            take = min(sz, base_amount - got)
        if take <= 0:
            break
        got += take
        cost += take * px
    return (cost / got if got else None), got, cost
