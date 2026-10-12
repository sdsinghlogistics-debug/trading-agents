"""Price action: market structure, support/resistance zones, and candle confirmation. Pure code, $0.

Structure timeframe: 6h candles (swing highs/lows, trend, levels).
Trigger timeframe:   1h candles (rejection / engulfing at the level).
Long-only (Coinbase spot), so we look for:
  A) Support bounce in an uptrend: price tags a support zone and prints a bullish rejection.
  B) Breakout & retest: price broke above resistance, pulls back to it, and holds with a rejection.
"""
from . import coinbase, config


def atr(c, n=14):
    tr = [max(c[i][2] - c[i][3], abs(c[i][2] - c[i - 1][4]), abs(c[i][3] - c[i - 1][4])) for i in range(1, len(c))]
    return sum(tr[-n:]) / min(n, len(tr)) if tr else 0


def swings(c, k=3):
    """Fractal pivots: a bar whose high/low is the extreme of k bars on each side."""
    hi, lo = [], []
    for i in range(k, len(c) - k):
        if c[i][2] == max(x[2] for x in c[i - k:i + k + 1]):
            if hi and i - hi[-1][0] <= k:              # same swing (equal highs on adjacent bars)
                if c[i][2] > hi[-1][1]:
                    hi[-1] = (i, c[i][2])
            else:
                hi.append((i, c[i][2]))
        if c[i][3] == min(x[3] for x in c[i - k:i + k + 1]):
            if lo and i - lo[-1][0] <= k:
                if c[i][3] < lo[-1][1]:
                    lo[-1] = (i, c[i][3])
            else:
                lo.append((i, c[i][3]))
    return hi, lo


def zones(points, width):
    """Cluster nearby pivot prices into zones; more touches = stronger level."""
    out = []
    for _, p in sorted(points, key=lambda x: x[1]):
        if out and p - out[-1]["hi"] <= width:
            z = out[-1]
            z["hi"], z["touches"] = max(z["hi"], p), z["touches"] + 1
            z["mid"] = (z["lo"] + z["hi"]) / 2
        else:
            out.append({"lo": p, "hi": p, "mid": p, "touches": 1})
    return out


def trend(hi, lo):
    if len(hi) < 2 or len(lo) < 2:
        return "unclear"
    hh, hl = hi[-1][1] > hi[-2][1], lo[-1][1] > lo[-2][1]
    lh, ll = hi[-1][1] < hi[-2][1], lo[-1][1] < lo[-2][1]
    return "up" if hh and hl else "down" if lh and ll else "range"


def candle(c):
    """Bullish confirmation on the last CLOSED candle: pin bar (hammer) or bullish engulfing."""
    if len(c) < 3:
        return None
    _, o, h, l, cl, _ = c[-2]          # last closed bar (c[-1] may still be forming)
    _, po, _, _, pc, _ = c[-3]
    rng, body = h - l, abs(cl - o)
    if rng <= 0:
        return None
    lower_wick = min(o, cl) - l
    if lower_wick >= 2 * max(body, rng * 0.05) and cl >= l + rng * 0.6:
        return "bullish pin bar"
    if cl > o and pc < po and cl >= po and o <= pc:
        return "bullish engulfing"
    return None


def analyze(pid):
    c6 = coinbase.candles(pid, "6h", 24 * 80)
    c1 = coinbase.candles(pid, "1h", 48)
    if len(c6) < 40 or len(c1) < 5:
        return {"product": pid, "error": "not enough candles"}
    px, a = c1[-1][4], atr(c6)
    hi, lo = swings(c6)
    t = trend(hi, lo)
    width = 0.5 * a
    sup = [z for z in zones(lo, width) if z["hi"] < px + width]
    res = [z for z in zones(hi, width) if z["lo"] > px]          # only levels still overhead
    # former resistance that price has since closed above = flipped support (breakout-retest)
    flipped = [z for z in zones(hi, width) if z["hi"] < px and any(x[4] > z["hi"] for x in c6[-12:])
               and any(x[4] <= z["hi"] for x in c6[-40:-12])]
    near_sup = max(sup + flipped, key=lambda z: z["hi"], default=None)
    next_res = min(res, key=lambda z: z["lo"], default=None)
    conf = candle(c1)
    at_level = near_sup is not None and near_sup["lo"] - width <= px <= near_sup["hi"] + width
    last_low = lo[-1][1] if lo else None
    out = {"product": pid, "price": px, "trend_6h": t, "atr_6h": round(a, 4),
           "support": round(near_sup["mid"], 4) if near_sup else None,
           "support_touches": near_sup["touches"] if near_sup else 0,
           "resistance": round(next_res["mid"], 4) if next_res else None,
           "last_swing_low": last_low, "candle_1h": conf, "setup": None}
    if t in ("up", "range") and at_level and conf:
        kind = "breakout-retest" if near_sup in flipped else "support bounce"
        if t == "range" and kind == "support bounce" and near_sup["touches"] < 2:
            return out | {"why_not": "range with untested support"}
        stop = near_sup["lo"] - 0.25 * a
        risk = px - stop
        target = next_res["lo"] if next_res else px + 2 * risk
        fees = 2 * config.FEE_PER_SIDE
        risk_f, reward_f = risk / px + fees, (target - px) / px - fees
        if reward_f < 2 * risk_f:                      # demand >= 2:1 reward:risk AFTER fees
            return out | {"why_not": f"target {target:.4f} pays {reward_f:.2%} vs risk {risk_f:.2%} after "
                                     f"{fees:.1%} fees; need 2:1"}
        out["setup"] = {"kind": kind, "stop": round(stop, 4), "target": round(target, 4),
                        "why": f"{kind} at {near_sup['mid']:.4f} ({near_sup['touches']} touches), 6h trend {t}, 1h {conf}"}
    return out


def confirms_long(pid):
    """Filter for the other agents: don't buy into a downtrend or right under resistance."""
    a = analyze(pid)
    if a.get("error"):
        return True, "no price-action data"
    if a["trend_6h"] == "down":
        return False, "6h structure is down (lower highs and lower lows)"
    if a["resistance"] and (a["resistance"] - a["price"]) < 0.5 * a["atr_6h"]:
        return False, f"buying right under resistance {a['resistance']}"
    return True, f"6h trend {a['trend_6h']}"


def structure_broken(pid, entry_ts=None):
    """Exit signal: a 6h close below the most recent swing low."""
    c6 = coinbase.candles(pid, "6h", 24 * 30)
    _, lo = swings(c6)
    return bool(lo) and c6[-2][4] < lo[-1][1]
