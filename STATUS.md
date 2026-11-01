# Agent status

_Updated 2026-11-01 14:59 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $979.19 | -2.08% | 2 | 6 | 1 | $-15.99 | $0.00 |
| priceaction | $1,000.00 | +0.00% | 0 | 0 | 0 | $+0.00 | $0.00 |
| trend | $992.63 | -0.74% | 0 | 2 | 0 | $-7.37 | $0.00 |

### follow: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| ETH-USD | 2,299.66 | 2,202.23 | 2,494.03 | $74 | 1/1 followed traders long, avg weight 17% |
| SOL-USD | 95.89 | 90.35 | 106.98 | $60 | 1/1 followed traders long, avg weight 13% |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| SOL-USD | timeout | $-3.60 | 1/1 followed traders long, avg weight 9% |
| BTC-USD | timeout | $-3.05 | 1/1 followed traders long, avg weight 13% |
| ETH-USD | stop | $-5.10 | 1/1 followed traders long, avg weight 8% |
| BTC-USD | timeout | $+0.43 | 1/1 followed traders long, avg weight 12% |
| ETH-USD | timeout | $-2.68 | 1/1 followed traders long, avg weight 10% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 77,921.51 | range | 77595.01 | 80770.07 | bullish engulfing | target 79257.1400 pays -0.69% vs risk 3.18% after 2.4% fees; need 2:1 |
| ETH-USD | 2,268.59 | down | 2170.03 | 2389.59 | - | downtrend: no longs |
| SOL-USD | 94.85 | range | 95.35 | 97.4 | - | waiting for a bullish 1h candle at support |
| PAXG-USD | 3,893.56 | up | 3885.92 | 4034.1 | bullish pin bar | target 4034.1000 pays 1.21% vs risk 2.80% after 2.4% fees; need 2:1 |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-4.64 | above rising 50d SMA (81541.56), pullback entry |
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
