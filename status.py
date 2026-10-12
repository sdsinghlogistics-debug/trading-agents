"""Writes STATUS.md: a readable scoreboard of every agent, shown on the repo's front page."""
import glob
import os
import json
import sqlite3
import time


def row(q, db, *a):
    r = db.execute(q, a).fetchone()
    return r[0] if r else None


out = [f"# Agent status\n\n_Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · paper trading_\n",
       "| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |",
       "|---|---|---|---|---|---|---|---|"]
details = []
for path in sorted(glob.glob("agent_*.db")):
    name = path[6:-3]
    db = sqlite3.connect(path)
    kv = {k: json.loads(v) for k, v in db.execute("select k, v from kv")}
    eq = row("select equity from equity order by ts desc limit 1", db) or kv.get("cash", 0)
    start = float(os.getenv("BANKROLL", 1000))
    opens = db.execute("select coin, entry, stop, target, notional, thesis from trades where closed is null").fetchall()
    closed = row("select count(*) from trades where closed is not null", db)
    wins = row("select count(*) from trades where pnl > 0", db)
    pnl = row("select coalesce(sum(pnl), 0) from trades where pnl is not null", db)
    ret = (eq / start - 1) if start else 0
    out.append(f"| {name} | ${eq:,.2f} | {ret:+.2%} | {len(opens)} | {closed} | {wins} | ${pnl:+,.2f} | ${kv.get('spend', 0):.2f} |")
    if opens:
        details.append(f"\n### {name}: open positions\n")
        details.append("| product | entry | stop | target | size | why |\n|---|---|---|---|---|---|")
        for c, e, s, t, n, th in opens:
            details.append(f"| {c} | {e:,.2f} | {s:,.2f} | {t:,.2f} | ${n:,.0f} | {(th or '')[:100]} |")
    last = db.execute("select coin, outcome, pnl, thesis from trades where closed is not null order by closed desc limit 5").fetchall()
    if last:
        details.append(f"\n### {name}: last closed trades\n")
        details.append("| product | result | P&L | why it was taken |\n|---|---|---|---|")
        for c, o, p, th in last:
            details.append(f"| {c} | {o} | ${p:+,.2f} | {(th or '')[:100]} |")

if len(out) == 3:
    out.append("| (no runs yet) | | | | | | | |")
open("STATUS.md", "w").write("\n".join(out + details) + "\n")
print("\n".join(out))
