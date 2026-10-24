# Agent status

_Updated 2026-10-24 10:49 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $989.90 | -1.01% | 2 | 3 | 1 | $-4.24 | $0.00 |
| priceaction | $1,000.00 | +0.00% | 0 | 0 | 0 | $+0.00 | $0.00 |
| trend | $993.80 | -0.62% | 1 | 1 | 0 | $-2.73 | $0.00 |

### follow: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| ETH-USD | 2,409.93 | 2,306.44 | 2,617.04 | $74 | 1/1 followed traders long, avg weight 8% |
| BTC-USD | 81,493.46 | 78,438.94 | 87,608.40 | $81 | 1/1 followed traders long, avg weight 13% |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $+0.43 | 1/1 followed traders long, avg weight 12% |
| ETH-USD | timeout | $-2.68 | 1/1 followed traders long, avg weight 10% |
| SOL-USD | timeout | $-1.99 | 1/1 followed traders long, avg weight 6% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 80,566.99 | down | 79910.69 | 81774.15 | - | downtrend: no longs |
| ETH-USD | 2,368.08 | down | 2319.275 | 2414.39 | bullish pin bar | downtrend: no longs |
| SOL-USD | 101.63 | range | 98.135 | 102.835 | - | waiting for a bullish 1h candle at support |
| PAXG-USD | 3,997.65 | down | 3989.21 | 4151.17 | - | downtrend: no longs |

### trend: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| BTC-USD | 81,680.06 | 79,277.64 | 86,475.72 | $93 | above rising 50d SMA (81541.56), pullback entry |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
