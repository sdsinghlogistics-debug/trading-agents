# Agent status

_Updated 2026-10-20 11:25 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $993.34 | -0.67% | 1 | 2 | 0 | $-4.67 | $0.00 |
| priceaction | $1,000.00 | +0.00% | 0 | 0 | 0 | $+0.00 | $0.00 |
| trend | $994.74 | -0.53% | 1 | 1 | 0 | $-2.73 | $0.00 |

### follow: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| BTC-USD | 81,788.34 | 77,938.01 | 89,488.97 | $70 | 1/1 followed traders long, avg weight 12% |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| ETH-USD | timeout | $-2.68 | 1/1 followed traders long, avg weight 10% |
| SOL-USD | timeout | $-1.99 | 1/1 followed traders long, avg weight 6% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 81,410.25 | range | 80506.24 | 82104.0 | - | waiting for a bullish 1h candle at support |
| ETH-USD | 2,382.71 | down | 2360.375 | 2443.86 | - | downtrend: no longs |
| SOL-USD | 104.16 | down | 102.835 | 105.505 | bullish engulfing | downtrend: no longs |
| PAXG-USD | 4,120.91 | range | 4122.175 | 4149.0 | bullish engulfing | target 4149.0000 pays -1.72% vs risk 2.47% after 2.4% fees; need 2:1 |

### trend: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| BTC-USD | 81,680.06 | 79,277.64 | 86,475.72 | $93 | above rising 50d SMA (81541.56), pullback entry |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
