"""The agent. Claude reasons through tools; code owns sizing, caps, stops and the kill switch."""
import json
import os
import time

from . import coinbase, config, hl, kelly, llm, news, rules, triggers
from .execution import Executor
from .ledger import Ledger

PRODUCTS = list(config.UNIVERSE)

SYSTEM = f"""You run a long-or-cash crypto book on Coinbase spot. Products: {", ".join(PRODUCTS)}.
You cannot short or use leverage. Round-trip fees are about {2 * config.FEE_PER_SIDE:.1%}, so only
multi-day moves of several percent are worth trading; scalps lose to fees.

Each cycle you get fresh headlines. Work like a careful discretionary trader:
1. Triage: most headlines don't matter. Pick the few that plausibly move one of your products over days.
2. Is it priced in? Check snapshot + candles. A widely reported story is usually already in the price.
   Look for slower second-order effects, macro shifts (rates, dollar, risk appetite -> BTC, gold),
   or positioning extremes.
3. Positioning (hyperliquid_positioning): crowded longs (high positive funding, rising OI) raise the risk
   of a flush; negative funding while price holds can fuel squeezes up.
4. Followed traders (followed_trader_positions): accounts with a statistically significant multi-month
   record. Their net exposure is evidence, not an order. Weigh it.
5. web_search to verify facts and base rates.
6. Only if you can name a concrete reason the price should rise, call propose_buy with a stop (where
   the thesis is wrong — outside normal daily noise), a target, and p = probability the target is hit
   before the stop within {config.MAX_HOLD_HOURS / 24:.0f} days. Be calibrated; claims of p > 0.6 on a
   symmetric bracket need strong evidence.
7. Review open positions (get_portfolio); call close_position if the thesis broke.

STRATEGY FOCUS ({config.STRATEGY}): {{focus}}

You never choose size: the system uses {config.KELLY_FRACTION:g}x Kelly with hard caps and may refuse.
Staying in cash is a good outcome when there's no edge. End with a 3-6 line decision log."""

FOCUS = {
    "news": "Trade only on news and macro catalysts (steps 1-2, 5). Use positioning and followed traders "
            "as confirmation, never as the reason.",
    "follow": "Your primary signal is the followed traders' net exposure. Buy only when a clear majority of "
              "them are net long a product with meaningful account weight, and no news contradicts it. "
              "Exit when their consensus flips. Ignore minor headlines.",
    "trend": "Ignore headlines unless they are major. Trade multi-week trends from daily candles: buy only "
             "when price is above its rising 50-day average and pulls back toward it; stop below the "
             "recent swing low.",
}
SYSTEM = SYSTEM.replace("{focus}", FOCUS.get(config.STRATEGY, FOCUS["news"]))

TOOLS = [
    {"type": "web_search_20250305", "name": "web_search", "max_uses": 8},
    {"name": "snapshot", "description": "Coinbase price, 24h change and volume for a product.",
     "input_schema": {"type": "object", "properties": {"product": {"type": "string"}}, "required": ["product"]}},
    {"name": "candles", "description": "Coinbase OHLCV. interval: 5m,15m,1h,6h,1d.",
     "input_schema": {"type": "object", "properties": {"product": {"type": "string"}, "interval": {"type": "string"},
                                                        "hours": {"type": "integer"}}, "required": ["product"]}},
    {"name": "hyperliquid_positioning", "description": "Perp funding, open interest and premium for the product's underlying.",
     "input_schema": {"type": "object", "properties": {"product": {"type": "string"}}, "required": ["product"]}},
    {"name": "followed_trader_positions", "description": "Live positions of the verified skilled traders, aggregated by coin.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_portfolio", "description": "Equity, cash, open positions with live PnL, forecast scorecard.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "propose_buy", "description": "Propose a bracketed spot buy. System sizes with Kelly and may refuse.",
     "input_schema": {"type": "object", "properties": {
         "product": {"type": "string"}, "stop": {"type": "number"}, "target": {"type": "number"},
         "p_target_first": {"type": "number"}, "confidence": {"type": "number", "description": "0-1 trust in your p vs breakeven"},
         "thesis": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}},
         "required": ["product", "stop", "target", "p_target_first", "confidence", "thesis"]}},
    {"name": "close_position", "description": "Sell an open position by trade id.",
     "input_schema": {"type": "object", "properties": {"trade_id": {"type": "integer"}, "reason": {"type": "string"}},
                      "required": ["trade_id", "reason"]}},
]


class Agent:
    def __init__(self):
        self.ledger = Ledger()
        self.exec = Executor()
        self.wallets = json.load(open(config.WALLETS_FILE)) if os.path.exists(config.WALLETS_FILE) else []

    # ----- accounting -----
    def mark(self, t):
        px = coinbase.snapshot(t["coin"])["price"]
        return px, t["size"] * px * (1 - config.FEE_PER_SIDE) - t["notional"]

    def equity(self):
        return self.ledger.get("cash") + sum(t["notional"] + self.mark(t)[1] for t in self.ledger.open_trades())

    def halted(self):
        eq = self.equity()
        return eq < self.ledger.day_start_equity(eq) * (1 - config.DAILY_LOSS_STOP)

    # ----- risk loop: every cycle, no LLM involved -----
    def manage(self):
        for t in self.ledger.open_trades():
            px, _ = self.mark(t)
            outcome = ("stop" if px <= t["stop"] else "target" if px >= t["target"]
                       else "timeout" if time.time() - t["opened"] > config.MAX_HOLD_HOURS * 3600 else None)
            if outcome:
                self._close(t, outcome)

    def _close(self, t, outcome):
        meta = json.loads(t["sources"] or "{}") if t["sources"] and t["sources"].startswith("{") else {}
        exit_px = self.exec.sell(t["coin"], t["size"], meta.get("bracket_id")) or coinbase.snapshot(t["coin"])["price"]
        proceeds = t["size"] * exit_px * (1 - config.FEE_PER_SIDE)
        pnl = proceeds - t["notional"]
        # cash already had `notional` removed at entry; return full proceeds
        self.ledger.close_trade(t["id"], exit_px, round(pnl, 2), outcome)
        self.ledger.set("cash", self.ledger.get("cash") + t["notional"])
        print(f"[close] #{t['id']} {t['coin']} {outcome} pnl {pnl:+.2f}")
        return pnl

    # ----- tools -----
    def tool(self, name, a):
        if name == "snapshot":
            return coinbase.snapshot(a["product"])
        if name == "candles":
            return coinbase.candles(a["product"], a.get("interval", "1h"), a.get("hours", 72))[-80:]
        if name == "hyperliquid_positioning":
            return hl.positioning(config.UNIVERSE.get(a["product"], a["product"].split("-")[0]))
        if name == "followed_trader_positions":
            agg = {}
            for w in self.wallets:  # all verified traders, incl. context-only
                try:
                    s = hl.positions(w["address"])
                except Exception:
                    continue
                for p in s["positions"]:
                    d = agg.setdefault(p["coin"], {"net_usd": 0, "traders": []})
                    d["net_usd"] += p["notional"] * (1 if p["size"] > 0 else -1)
                    d["traders"].append(f'{w["label"]}: {"long" if p["size"] > 0 else "short"} '
                                        f'{p["notional"] / max(s["account_value"], 1):.0%} of account')
            return agg or "followed traders are flat"
        if name == "get_portfolio":
            pos = []
            for t in self.ledger.open_trades():
                px, upnl = self.mark(t)
                pos.append({k: t[k] for k in ("id", "coin", "entry", "stop", "target", "notional", "thesis")}
                           | {"price": px, "upnl": round(upnl, 2)})
            return {"equity": round(self.equity(), 2), "cash": round(self.ledger.get("cash"), 2),
                    "open": pos, "scorecard": self.ledger.scorecard()}
        if name == "close_position":
            t = next((t for t in self.ledger.open_trades() if t["id"] == a["trade_id"]), None)
            return {"pnl": round(self._close(t, "manual"), 2)} if t else {"error": "no such open position"}
        if name == "propose_buy":
            return self.propose(a)
        return {"error": "unknown tool"}

    def propose(self, a):
        pid = a["product"]
        if pid not in config.UNIVERSE:
            return {"refused": f"{pid} not in universe {PRODUCTS}"}
        if self.halted():
            return {"refused": "daily loss stop hit; no new risk today"}
        opens = self.ledger.open_trades()
        if len(opens) >= config.MAX_POSITIONS or any(t["coin"] == pid for t in opens):
            return {"refused": "position limit, or already holding this product"}
        if a["confidence"] < config.MIN_CONFIDENCE:
            return {"refused": "confidence below minimum (forecast not traded)"}
        px = coinbase.snapshot(pid)["price"]
        stop, target = float(a["stop"]), float(a["target"])
        dvol = coinbase.realized_vol(pid) or 0
        if dvol and (px - stop) / px < 1.0 * dvol:
            return {"refused": f"stop is inside one day of normal noise (daily vol {dvol:.2%}); widen or pass"}
        s = kelly.size(a["p_target_first"], px, stop, target, self.equity(), a["confidence"],
                       sum(t["notional"] for t in opens))
        return self._enter(pid, stop, target, s, a)

    def _enter(self, pid, stop, target, s, a):
        if not s["ok"]:
            return {"refused": s["reason"]}
        amount = min(s["amount"], self.ledger.get("cash"))
        fill = self.exec.buy(pid, amount, stop, target)
        if not fill["filled"]:
            return {"refused": fill["reason"]}
        self.ledger.open_trade(mode=config.MODE, coin=pid, side="long", entry=fill["entry"], stop=stop, target=target,
                               notional=fill["cost"], size=fill["size"] * (1 - config.FEE_PER_SIDE),
                               p_model=a.get("p_target_first"), p_adj=s["p_adj"], breakeven_p=s["breakeven_p"],
                               confidence=a.get("confidence"), thesis=a["thesis"],
                               sources=json.dumps({"bracket_id": fill.get("bracket_id"), "links": a.get("sources", [])}))
        self.ledger.set("cash", self.ledger.get("cash") - fill["cost"])
        print(f"[buy] {pid} ${fill['cost']:.0f} @ {fill['entry']:.2f} | risk ${s['risk_usd']} | {a['thesis'][:90]}")
        return {"opened": True, **fill, **s}

    # ----- spend tracking -----
    def _spend(self, usd):
        month = time.strftime("%Y-%m")
        if self.ledger.get("spend_month") != month:
            self.ledger.set("spend_month", month)
            self.ledger.set("spend", 0.0)
        self.ledger.set("spend", (self.ledger.get("spend") or 0) + usd)

    def over_budget(self):
        return (self.ledger.get("spend_month") == time.strftime("%Y-%m")
                and (self.ledger.get("spend") or 0) >= config.MONTHLY_BUDGET)

    # ----- AI path (news strategy) -----
    def think(self, context):
        msgs = [{"role": "user", "content": f"UTC now {time.strftime('%Y-%m-%d %H:%M')}.\n{context}\n\nRun your cycle."}]
        for _ in range(config.MAX_AGENT_STEPS):
            r, spent = llm.create(config.MODEL, SYSTEM, msgs, TOOLS)
            self._spend(spent)
            msgs.append({"role": "assistant", "content": r.content})
            calls = [b for b in r.content if b.type == "tool_use"]
            if r.stop_reason != "tool_use" or not calls:
                return "".join(b.text for b in r.content if b.type == "text")
            res = []
            for c in calls:
                try:
                    out = self.tool(c.name, c.input)
                except Exception as e:
                    out = {"error": str(e)}
                res.append({"type": "tool_result", "tool_use_id": c.id, "content": json.dumps(out, default=str)[:8000]})
            msgs.append({"role": "user", "content": res})
        return "step limit reached"

    def news_cycle(self):
        items = news.fetch(self.ledger.seen())
        self.ledger.mark_seen(items)
        heads = triggers.relevant_headlines(items)
        moves, prices = triggers.price_moves(self.ledger)
        heartbeat = triggers.heartbeat_due(self.ledger) and self.ledger.open_trades()
        if not (heads or moves or heartbeat):
            return "quiet: no relevant headlines or big moves (no AI call, $0)"
        if self.over_budget():
            return f"monthly AI budget ${config.MONTHLY_BUDGET} reached; rules-only until next month"
        text = "\n".join(f"- {time.strftime('%H:%M', time.gmtime(n['ts']))}Z [{n['source']}] {n['title']}" for n in heads)
        text += ("\nPrice moves: " + "; ".join(moves)) if moves else ""
        if not heartbeat:
            verdict, spent = llm.triage(text)
            self._spend(spent)
            if not verdict.get("act"):
                return f"triage pass ({config.TRIAGE_MODEL}): {verdict.get('why', '')}"
            text += f"\nTriage flagged: {verdict.get('products')} - {verdict.get('why')}"
        else:
            text += "\nDaily review: check open positions."
        self.ledger.set("last_ai_run", time.time())
        self.ledger.set("last_seen_prices", prices)
        return self.think(text)

    # ----- zero-token paths (follow / trend) -----
    def rules_cycle(self):
        opens = self.ledger.open_trades()
        held = {t["coin"] for t in opens}
        if config.STRATEGY == "follow":
            sigs, flips = rules.follow_signals(self.wallets)
            for t in opens:
                if t["coin"] in flips:
                    self._close(t, "consensus_flip")
        else:
            sigs = rules.trend_signals()
        if self.halted():
            return "daily loss stop hit"
        p, n = rules.empirical_p(self.ledger)
        log = []
        for sg in sigs:
            pid = sg["product"]
            if pid in held or len(self.ledger.open_trades()) >= config.MAX_POSITIONS:
                continue
            px, stop, target = rules.bracket(pid, sg.get("stop"))
            deployed = sum(t["notional"] for t in self.ledger.open_trades())
            s = (kelly.size(p, px, stop, target, self.equity(), 1.0, deployed) if p is not None
                 else kelly.size_fixed(px, stop, self.equity(), deployed))
            r = self._enter(pid, stop, target, s, {"thesis": sg["why"], "p_target_first": p, "confidence": 1.0})
            log.append(f"{pid}: {r.get('refused') or 'opened'}")
        sizing = f"empirical Kelly p={p:.2f} (n={n})" if p is not None else f"fixed {config.FIXED_RISK:.1%} risk until {config.MIN_TRADES_FOR_KELLY} trades (have {n})"
        return f"{len(sigs)} signal(s); {sizing}; " + ("; ".join(log) or "no entries")

    def cycle(self):
        self.manage()
        log = self.news_cycle() if config.STRATEGY == "news" else self.rules_cycle()
        eq = self.equity()
        self.ledger.snapshot_equity(eq)
        spend = self.ledger.get("spend") or 0
        print(f"[{time.strftime('%H:%M')}] {config.STRATEGY} | equity ${eq:,.2f} | AI spend this month ${spend:.2f}\n{log}\n")
