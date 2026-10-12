"""Coinbase spot execution. Paper walks the real book; live uses the Advanced Trade API.

Live opens with a market buy, then attaches an exchange-side bracket (take-profit limit + stop trigger),
so stops still work if this program or your computer goes down.
"""
import os
import uuid

from . import coinbase, config


class Executor:
    def __init__(self):
        self.live = config.MODE == "live"
        self.cb = None
        if self.live:
            if not config.LIVE_ACK:
                raise SystemExit("MODE=live needs I_UNDERSTAND=1. Stay in paper until the scorecard shows an edge.")
            from coinbase.rest import RESTClient  # pip install coinbase-advanced-py
            # Create a key with View + Trade permissions only. Never enable Transfer/withdraw.
            self.cb = RESTClient(api_key=os.environ["CB_API_KEY"], api_secret=os.environ["CB_API_SECRET"])

    @staticmethod
    def _round(x, inc):
        d = len(inc.split(".")[1].rstrip("0")) if "." in inc else 0
        return f"{(int(x * 10**d) / 10**d):.{d}f}"

    def buy(self, pid, quote_amount, stop, target):
        bids, asks = coinbase.book(pid)
        avg, base, cost = coinbase.walk(asks, quote_amount=quote_amount)
        if not avg:
            return {"filled": False, "reason": "empty book"}
        mid = (bids[0][0] + asks[0][0]) / 2
        bracket_id = None
        if self.live:
            snap = coinbase.snapshot(pid)
            r = self.cb.market_order_buy(client_order_id=str(uuid.uuid4()), product_id=pid,
                                         quote_size=self._round(quote_amount, snap["quote_increment"]))
            if not r.success:
                return {"filled": False, "reason": str(r.error_response)}
            fill = self.cb.get_order(r.success_response["order_id"]).order
            base = float(fill.filled_size)
            avg = float(fill.average_filled_price)
            cost = base * avg
            br = self.cb.trigger_bracket_order_gtc_sell(
                client_order_id=str(uuid.uuid4()), product_id=pid,
                base_size=self._round(base * (1 - config.FEE_PER_SIDE), snap["base_increment"]),
                limit_price=self._round(target, snap["quote_increment"]),
                stop_trigger_price=self._round(stop, snap["quote_increment"]))
            bracket_id = br.success_response["order_id"] if br.success else None
        return {"filled": True, "entry": avg, "size": base, "cost": cost,
                "slippage_bps": round((avg / mid - 1) * 1e4, 1), "bracket_id": bracket_id}

    def sell(self, pid, base, bracket_id=None):
        bids, _ = coinbase.book(pid)
        avg, _, _ = coinbase.walk(bids, base_amount=base)
        if self.live:
            if bracket_id:
                self.cb.cancel_orders(order_ids=[bracket_id])
            snap = coinbase.snapshot(pid)
            self.cb.market_order_sell(client_order_id=str(uuid.uuid4()), product_id=pid,
                                      base_size=self._round(base, snap["base_increment"]))
        return avg
