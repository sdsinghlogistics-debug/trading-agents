# Agent status

_Updated 2026-10-30 19:14 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $979.05 | -2.10% | 2 | 5 | 1 | $-12.39 | $0.00 |
| priceaction | $1,000.00 | +0.00% | 0 | 0 | 0 | $+0.00 | $0.00 |
| trend | $992.63 | -0.74% | 0 | 2 | 0 | $-7.37 | $0.00 |

### follow: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| SOL-USD | 99.78 | 93.70 | 111.95 | $58 | 1/1 followed traders long, avg weight 9% |
| ETH-USD | 2,299.66 | 2,202.23 | 2,494.03 | $74 | 1/1 followed traders long, avg weight 17% |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-3.05 | 1/1 followed traders long, avg weight 13% |
| ETH-USD | stop | $-5.10 | 1/1 followed traders long, avg weight 8% |
| BTC-USD | timeout | $+0.43 | 1/1 followed traders long, avg weight 12% |
| ETH-USD | timeout | $-2.68 | 1/1 followed traders long, avg weight 10% |
| SOL-USD | timeout | $-1.99 | 1/1 followed traders long, avg weight 6% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 76,332.53 | up | 62549.695 | 82435.43 | - | waiting for a bullish 1h candle at support |
| ETH-USD | 2,229.07 | down | 2170.03 | 2401.99 | - | downtrend: no longs |
| SOL-USD | 94.15 | range | 92.68 | 97.4 | bullish pin bar | target 97.4000 pays 1.05% vs risk 5.25% after 2.4% fees; need 2:1 |
| PAXG-USD | 3,891.13 | up | - | 4034.1 | - | waiting for a bullish 1h candle at support |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-4.64 | above rising 50d SMA (81541.56), pullback entry |
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
