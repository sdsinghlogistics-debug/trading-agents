"""Free, code-only checks that decide whether the AI needs to wake up at all."""
import re
import time

from . import coinbase, config

KEYWORDS = {
    "BTC": r"\b(bitcoin|btc|crypto|etf flows?|saylor|microstrategy|strategy inc)\b",
    "ETH": r"\b(ethereum|eth|ether|crypto)\b",
    "SOL": r"\b(solana|sol|crypto)\b",
    "PAXG": r"\b(gold|bullion|safe.haven)\b",
}
MACRO = (r"\b(fed|fomc|powell|rate (cut|hike)|interest rates?|cpi|inflation|jobs report|payrolls|"
         r"tariffs?|treasury yields?|recession|dollar index|dxy|sec|etf|stablecoin|hack|exploit|war|sanctions)\b")


def relevant_headlines(items):
    """Headlines that mention a product or a market-moving macro theme."""
    out = []
    for n in items:
        text = f"{n['title']} {n['summary']}".lower()
        hits = [c for c, rx in KEYWORDS.items() if re.search(rx, text)]
        if hits or re.search(MACRO, text):
            out.append(n | {"hits": hits or ["macro"]})
    return out


def price_moves(ledger):
    """Products that moved more than PRICE_TRIGGER since the AI last looked."""
    last = ledger.get("last_seen_prices") or {}
    moves, now = [], {}
    for pid in config.UNIVERSE:
        try:
            px = coinbase.snapshot(pid)["price"]
        except Exception:
            continue
        now[pid] = px
        if pid in last and abs(px / last[pid] - 1) >= config.PRICE_TRIGGER:
            moves.append(f"{pid} {px / last[pid] - 1:+.1%} since last AI check")
    return moves, now


def heartbeat_due(ledger):
    """Force one AI review per HEARTBEAT_HOURS even when quiet (to manage open positions)."""
    return time.time() - (ledger.get("last_ai_run") or 0) > config.HEARTBEAT_HOURS * 3600
