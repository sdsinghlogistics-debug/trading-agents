"""SQLite memory: headlines seen, every forecast, open/closed trades, equity curve."""
import json
import sqlite3
import time

from . import config

SCHEMA = """
create table if not exists seen(id text primary key, ts int);
create table if not exists trades(
  id integer primary key, opened int, closed int, mode text, coin text, side text,
  entry real, stop real, target real, notional real, size real,
  p_model real, p_adj real, breakeven_p real, confidence real, thesis text, sources text,
  exit real, pnl real, outcome text);
create table if not exists equity(ts int, equity real);
create table if not exists kv(k text primary key, v text);
"""


class Ledger:
    def __init__(self, path=config.DB_PATH):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        if self.get("cash") is None:
            self.set("cash", config.BANKROLL)

    def get(self, k):
        r = self.db.execute("select v from kv where k=?", (k,)).fetchone()
        return json.loads(r["v"]) if r else None

    def set(self, k, v):
        self.db.execute("insert or replace into kv values(?,?)", (k, json.dumps(v)))
        self.db.commit()

    def seen(self):
        return {r["id"] for r in self.db.execute("select id from seen where ts>?", (time.time() - 3 * 86400,))}

    def mark_seen(self, items):
        self.db.executemany("insert or ignore into seen values(?,?)", [(i["id"], int(time.time())) for i in items])
        self.db.commit()

    def open_trade(self, **t):
        cols = ",".join(t)
        self.db.execute(f"insert into trades({cols},opened) values({','.join('?' * len(t))},?)",
                        (*t.values(), int(time.time())))
        self.db.commit()

    def open_trades(self):
        return [dict(r) for r in self.db.execute("select * from trades where closed is null")]

    def close_trade(self, tid, exit_px, pnl, outcome):
        self.db.execute("update trades set closed=?, exit=?, pnl=?, outcome=? where id=?",
                        (int(time.time()), exit_px, pnl, outcome, tid))
        self.set("cash", self.get("cash") + pnl)

    def snapshot_equity(self, eq):
        self.db.execute("insert into equity values(?,?)", (int(time.time()), eq))
        self.db.commit()

    def day_start_equity(self, eq):
        day = time.strftime("%Y-%m-%d")
        if self.get("day") != day:
            self.set("day", day)
            self.set("day_start", eq)
        return self.get("day_start")

    def scorecard(self):
        """Did the model's probabilities beat the breakeven prices it traded at? Brier on TP-vs-SL outcomes."""
        rows = [dict(r) for r in self.db.execute("select * from trades where outcome in ('target','stop')")]
        if not rows:
            return {"closed": 0}
        y = [1.0 if r["outcome"] == "target" else 0.0 for r in rows]
        bm = sum((r["p_adj"] - v) ** 2 for r, v in zip(rows, y)) / len(rows)
        bb = sum((r["breakeven_p"] - v) ** 2 for r, v in zip(rows, y)) / len(rows)
        pnl = [r["pnl"] for r in self.db.execute("select pnl from trades where pnl is not null")]
        return {"closed": len(rows), "hit_rate": round(sum(y) / len(y), 3),
                "brier_model": round(bm, 4), "brier_breakeven": round(bb, 4),
                "model_beats_breakeven": bm < bb, "realized_pnl": round(sum(pnl), 2),
                "note": "Need ~100+ closed trades before trusting this."}
