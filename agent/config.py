"""Every tunable in one place. Override with environment variables."""
import os


def _f(k, d):
    return float(os.getenv(k, d))


# Mode: "paper" fills against Coinbase's live order book and never sends orders.
# "live" places real orders through the Coinbase Advanced Trade API with YOUR key. Needs I_UNDERSTAND=1.
MODE = os.getenv("MODE", "paper")
LIVE_ACK = os.getenv("I_UNDERSTAND") == "1"

# --- Cost controls -------------------------------------------------------------
# The loop runs free code every CYCLE_SECONDS. The AI is called only when a trigger fires.
MODEL = os.getenv("MODEL", "claude-sonnet-5-5")              # full analysis (only after triage says yes)
TRIAGE_MODEL = os.getenv("TRIAGE_MODEL", "claude-haiku-5-5")  # or "ollama:qwen2.5:14b" for free local triage
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", 12))
CYCLE_SECONDS = int(os.getenv("CYCLE_SECONDS", 600))          # free checks every 10 min
PRICE_TRIGGER = float(os.getenv("PRICE_TRIGGER", 0.03))        # wake AI on a 3% move
HEARTBEAT_HOURS = float(os.getenv("HEARTBEAT_HOURS", 24))      # at least one AI review per day
MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", 10))        # USD; AI calls stop when reached

# Rule strategies (follow / trend) use no AI at all.
FOLLOW_MIN_TRADERS = int(os.getenv("FOLLOW_MIN_TRADERS", 1))      # only one verified trader is copyable today
FOLLOW_CONSENSUS = float(os.getenv("FOLLOW_CONSENSUS", 1.0))
FOLLOW_MIN_WEIGHT = float(os.getenv("FOLLOW_MIN_WEIGHT", 0.05))   # position >= 5% of their account
MIN_TRADES_FOR_KELLY = int(os.getenv("MIN_TRADES_FOR_KELLY", 30))
FIXED_RISK = float(os.getenv("FIXED_RISK", 0.005))             # 0.5% risk per trade until Kelly has data

# Execution venue: Coinbase spot (long or cash; Canadian accounts are spot-only below $5M net assets).
# Signal venue: Hyperliquid public data (followed traders, funding, open interest) — read-only.
QUOTE = os.getenv("QUOTE", "USD")
UNIVERSE = {  # Coinbase product -> Hyperliquid coin used for positioning signals
    f"BTC-{QUOTE}": "BTC",
    f"ETH-{QUOTE}": "ETH",
    f"SOL-{QUOTE}": "SOL",
    f"PAXG-{QUOTE}": "PAXG",   # tokenized gold
}

# Bankroll & risk -----------------------------------------------------------
BANKROLL = _f("BANKROLL", 1000)                     # paper starting equity in QUOTE
KELLY_FRACTION = _f("KELLY_FRACTION", 0.25)          # quarter Kelly
MAX_RISK_PER_TRADE = _f("MAX_RISK_PER_TRADE", 0.02)  # max equity lost if the stop hits
MAX_GROSS = _f("MAX_GROSS", 1.0)                     # spot: can't deploy more than 100% of equity
MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", 4))
DAILY_LOSS_STOP = _f("DAILY_LOSS_STOP", 0.05)
MIN_EDGE = _f("MIN_EDGE", 0.05)                      # expected value per $ risked, after fees
MIN_CONFIDENCE = _f("MIN_CONFIDENCE", 0.5)
MAX_HOLD_HOURS = _f("MAX_HOLD_HOURS", 168)           # 7 days: fees make short holds uneconomic

# Coinbase Advanced fees are tiered by 30-day volume. Low tiers are expensive (taker ~1.2%, maker ~0.6%).
# Set this to YOUR current tier — it drives every sizing decision.
FEE_PER_SIDE = _f("FEE_PER_SIDE", 0.012)

# Which strategy this process runs: news | follow | trend. Run one process per strategy.
STRATEGY = os.getenv("STRATEGY", "news")  # news | follow | trend | priceaction
PA_FILTER = os.getenv("PA_FILTER", "1") == "1"   # every agent must agree with price action before buying
DB_PATH = os.getenv("DB_PATH", f"agent_{STRATEGY}.db")
WALLETS_FILE = os.getenv("WALLETS_FILE", "skilled_wallets.json")
HL_API = "https://api.hyperliquid.xyz"
CB_API = "https://api.coinbase.com/api/v3/brokerage"

NEWS_FEEDS = [
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.fxstreet.com/rss/news",
    "https://www.kitco.com/rss/KitcoNews.xml",
]
