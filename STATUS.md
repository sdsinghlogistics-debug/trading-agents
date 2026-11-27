# Agent status

_Updated 2026-11-27 08:12 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $971.46 | -2.85% | 0 | 9 | 1 | $-28.54 | $0.00 |
| priceaction | $994.93 | -0.51% | 0 | 1 | 0 | $-5.07 | $0.00 |
| trend | $992.63 | -0.74% | 0 | 2 | 0 | $-7.37 | $0.00 |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | stop | $-5.07 | 1/1 followed traders long, avg weight 19% |
| SOL-USD | stop | $-5.13 | 1/1 followed traders long, avg weight 13% |
| ETH-USD | timeout | $-2.35 | 1/1 followed traders long, avg weight 17% |
| SOL-USD | timeout | $-3.60 | 1/1 followed traders long, avg weight 9% |
| BTC-USD | timeout | $-3.05 | 1/1 followed traders long, avg weight 13% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 61,774.39 | range | 61973.085 | 64278.825 | - | waiting for a bullish 1h candle at support |
| ETH-USD | 1,733.84 | range | 1740.095 | 1815.7 | bullish pin bar | target 1815.7000 pays 2.32% vs risk 3.13% after 2.4% fees; need 2:1 |
| SOL-USD | 73.17 | range | 71.42 | 73.24 | bullish engulfing | not at a support level |
| PAXG-USD | 3,646.84 | down | 3597.65 | 3677.68 | - | downtrend: no longs |

### priceaction: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| SOL-USD | stop | $-5.07 | breakout-retest at 73.2400 (1 touches), 6h trend range, 1h bullish pin bar |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-4.64 | above rising 50d SMA (81541.56), pullback entry |
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
