"""Kelly sizing for a bracketed long spot trade.

The model gives p = probability price hits the target before the stop.
After round-trip fees, win = +tp, loss = -sl (as fractions of the amount invested).
Full Kelly fraction of equity *risked* is f* = p - (1 - p) / b, with b = tp / sl.
Amount invested = (f * equity) / sl, because a stop-out loses invested * sl.
"""
from . import config


def size_fixed(entry, stop, equity, deployed):
    """Rule strategies before they have a track record: risk a small fixed % of equity."""
    sl = (entry - stop) / entry + 2 * config.FEE_PER_SIDE
    amount = min(config.FIXED_RISK * equity / sl, max(0.0, config.MAX_GROSS * equity - deployed))
    if amount < 10:
        return {"ok": False, "reason": "size below $10"}
    return {"ok": True, "amount": round(amount, 2), "risk_usd": round(amount * sl, 2),
            "kelly_full": None, "p_adj": None, "breakeven_p": None, "ev_per_risk": None}


def size(p, entry, stop, target, equity, confidence, deployed):
    fees = 2 * config.FEE_PER_SIDE
    sl = (entry - stop) / entry + fees
    tp = (target - entry) / entry - fees
    if not stop < entry < target:
        return {"ok": False, "reason": "spot is long-only: need stop < price < target"}
    if tp <= 0:
        return {"ok": False, "reason": f"target is inside round-trip fees ({fees:.2%}); widen it"}
    p0 = sl / (sl + tp)                       # breakeven probability after fees
    p_adj = p0 + confidence * (p - p0)        # shrink toward breakeven by (1 - confidence)
    b = tp / sl
    f_full = p_adj - (1 - p_adj) / b
    ev_per_risk = (p_adj * tp - (1 - p_adj) * sl) / sl
    if f_full <= 0:
        return {"ok": False, "reason": f"no edge: p_adj {p_adj:.3f} <= breakeven {p0:.3f} after fees"}
    if ev_per_risk < config.MIN_EDGE:
        return {"ok": False, "reason": f"edge {ev_per_risk:.3f} per $ risked < {config.MIN_EDGE}"}
    risk = min(f_full * config.KELLY_FRACTION, config.MAX_RISK_PER_TRADE) * equity
    amount = min(risk / sl, max(0.0, config.MAX_GROSS * equity - deployed))
    if amount < 10:
        return {"ok": False, "reason": "size after caps below $10"}
    return {"ok": True, "amount": round(amount, 2), "risk_usd": round(amount * sl, 2),
            "kelly_full": round(f_full, 4), "p_adj": round(p_adj, 4), "breakeven_p": round(p0, 4),
            "ev_per_risk": round(ev_per_risk, 4)}
