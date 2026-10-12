# Crypto agents (Coinbase spot, paper-first, low token cost)

Three strategies, one process each, each with its own paper ledger:

| STRATEGY | what it does | AI cost |
|---|---|---|
| `news`   | Free code scans news + prices every 10 min. Only relevant headlines or a 3%+ move go to a cheap triage model; only if triage says "act" does the full model analyse and propose a trade. | ~$0.50–3 / month typical, hard-capped by `MONTHLY_BUDGET` (default $10) |
| `follow` | Buys when ≥70% of the verified Hyperliquid traders are long a product with real account weight; exits when their consensus flips. Pure code. | $0 |
| `trend`  | Buys pullbacks to a rising 50-day average, stop under the 20-day low, target 2× risk. Pure code. | $0 |
| `priceaction` | Reads 6h market structure (higher highs/lows), clusters swing points into support/resistance zones, and buys a **support bounce** or **breakout-retest** only when the last closed 1h candle is a bullish pin bar or engulfing. Stop below the zone, target at the next resistance, and only if it pays ≥ 2:1 **after fees**. Exits early if a 6h candle closes below the last swing low. | $0 |

**Price-action filter (all agents):** before any agent buys, the code checks the chart. No buying into a
6h downtrend (lower highs + lower lows) or right under resistance. Turn off with `PA_FILTER=0`.

The code owns all risk: ¼-Kelly sizing, max 2% equity risk per trade, 100% max deployed, 5% daily
loss stop, stop/target on every position, 7-day max hold. Rule strategies risk a fixed 0.5% per trade
until they have 30 closed trades, then size by Kelly from their *own* realized hit rate.

## Running on GitHub (nothing to install)
The workflow in `.github/workflows/agents.yml` runs all agents **every hour** on GitHub's servers,
saves each agent's paper ledger back into this repo, and rewrites **STATUS.md** with the scoreboard.

1. **Actions** tab → enable workflows if asked → **crypto agents** → **Run workflow** to test it now.
2. Open **STATUS.md** after the run (about 1–2 minutes) to see equity, positions and the reason for every trade.
3. Optional, for the news agent: **Settings → Secrets and variables → Actions → New repository secret**,
   name `ANTHROPIC_API_KEY`, paste your key. Without it, only the free follow/trend agents run.
4. Optional: under **Variables**, add `MONTHLY_BUDGET` (default 10) to cap AI spend.

Minutes: public repos run free. Private repos get 2,000 free minutes/month; hourly runs use ~1,000–1,500.

## Setup on your own machine (alternative)
```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # only the news agent needs this
STRATEGY=follow python run.py            # $0
STRATEGY=trend  python run.py            # $0
STRATEGY=news   python run.py            # pennies
```
Run each in its own Terminal tab (or with `nohup ... &` on a server).

## Make the news agent free: local triage with Ollama
Install Ollama (ollama.com), then `ollama pull qwen2.5:14b`, then:
```
TRIAGE_MODEL=ollama:qwen2.5:14b STRATEGY=news python run.py
```
The local model does the screening at $0; Claude is only called for the rare "act" cases.

## Cost knobs
| var | default | effect |
|---|---|---|
| MONTHLY_BUDGET | 10 | AI calls stop for the month at this $ amount |
| MODEL | claude-sonnet-5-5 | full analysis model (claude-haiku-5-5 is cheapest) |
| TRIAGE_MODEL | claude-haiku-5-5 | or `ollama:<model>` for free |
| PRICE_TRIGGER | 0.03 | wake the AI on a move this size |
| HEARTBEAT_HOURS | 24 | one forced review per day, only if positions are open |

Prompt caching is on, so the repeated instructions bill at ~10% after the first call.

## Trading settings
| var | default | meaning |
|---|---|---|
| FEE_PER_SIDE | 0.012 | your Coinbase fee tier, drives all sizing |
| BANKROLL | 1000 | paper starting equity |
| KELLY_FRACTION | 0.25 | fraction of full Kelly |

## Judging the agents
Run paper for 4+ weeks. Each ledger (`agent_news.db`, etc.) records every trade with its thesis.
Keep only strategies whose results beat simply holding BTC over 30+ closed trades.

## Going live (only after paper proves an edge)
`pip install coinbase-advanced-py`; create a Coinbase Developer Platform key with **View + Trade only (no Transfer)**;
then `MODE=live I_UNDERSTAND=1 CB_API_KEY=... CB_API_SECRET=... python run.py`.
Live entries attach an exchange-side bracket order, so stops work even if your computer is off.

`skilled_wallets.json` = the verified traders the `follow` agent watches.
