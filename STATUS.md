# Agent status

_Updated 2026-11-21 23:05 UTC · paper trading_

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
| BTC-USD | 60,000.68 | down | - | 64023.69 | - | downtrend: no longs |
| ETH-USD | 1,677.07 | down | 1535.37 | 1815.7 | - | downtrend: no longs |
| SOL-USD | 70.08 | range | 69.87 | 73.24 | - | waiting for a bullish 1h candle at support |
| PAXG-USD | 3,542.86 | down | 3487.83 | 3881.025 | - | downtrend: no longs |

### priceaction: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| SOL-USD | stop | $-5.07 | breakout-retest at 73.2400 (1 touches), 6h trend range, 1h bullish pin bar |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-4.64 | above rising 50d SMA (81541.56), pullback entry |
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
