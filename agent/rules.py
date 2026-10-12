"""Zero-token strategies: follow the verified traders, and a daily trend rule.

These have no model to estimate a win probability, so sizing starts at a small fixed risk and switches
to Kelly from the strategy's OWN realized hit rate once it has enough closed trades (empirical Kelly).
"""
from . import coinbase, config, hl


def sma(xs, n):
    return sum(xs[-n:]) / n if len(xs) >= n else None


def empirical_p(ledger):
    """Laplace-smoothed hit rate of this strategy's closed bracket trades; None until enough history."""
    rows = list(ledger.db.execute("select outcome from trades where outcome in ('target','stop')"))
    n = len(rows)
    if n < config.MIN_TRADES_FOR_KELLY:
        return None, n
    wins = sum(1 for r in rows if r["outcome"] == "target")
    return (wins + 1) / (n + 2), n


def follow_signals(wallets):
    """Per product: share of followed traders long vs short, weighted by % of their account."""
    tally = {}
    for w in [w for w in wallets if w.get("follow")]:
        try:
            s = hl.positions(w["address"])
        except Exception:
            continue
        av = max(s["account_value"], 1)
        for p in s["positions"]:
            t = tally.setdefault(p["coin"], {"long": 0, "short": 0, "weight": 0.0})
            t["long" if p["size"] > 0 else "short"] += 1
            t["weight"] += (1 if p["size"] > 0 else -1) * p["notional"] / av
    sigs = []
    for pid, coin in config.UNIVERSE.items():
        t = tally.get(coin)
        if not t:
            continue
        n = t["long"] + t["short"]
        if n >= config.FOLLOW_MIN_TRADERS and t["long"] / n >= config.FOLLOW_CONSENSUS and t["weight"] / n >= config.FOLLOW_MIN_WEIGHT:
            sigs.append({"product": pid, "why": f"{t['long']}/{n} followed traders long, avg weight {t['weight'] / n:.0%}"})
    flips = [pid for pid, coin in config.UNIVERSE.items()
             if coin in tally and tally[coin]["short"] > tally[coin]["long"]]
    return sigs, flips


def trend_signals():
    sigs = []
    for pid in config.UNIVERSE:
        cs = coinbase.candles(pid, "1d", 24 * 120)
        closes = [c[4] for c in cs]
        lows = [c[3] for c in cs]
        s50, s50_prev = sma(closes, 50), sma(closes[:-5], 50)
        if not s50 or not s50_prev:
            continue
        px = closes[-1]
        if s50 > s50_prev and s50 < px <= s50 * 1.03:   # rising trend, pulled back near the average
            stop = min(lows[-20:]) * 0.995
            sigs.append({"product": pid, "stop": stop, "why": f"above rising 50d SMA ({s50:.2f}), pullback entry"})
    return sigs


def bracket(pid, stop=None):
    """Default bracket from daily volatility: stop 2 vol below, target at 2R (reward = 2x risk)."""
    px = coinbase.snapshot(pid)["price"]
    vol = coinbase.realized_vol(pid) or 0.03
    stop = stop or px * (1 - 2 * vol)
    return px, stop, px + 2 * (px - stop)
