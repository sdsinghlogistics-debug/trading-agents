# Agent status

_Updated 2026-10-29 00:49 UTC · paper trading_

| agent | equity | return | open | closed | wins | realized P&L | AI spend (month) |
|---|---|---|---|---|---|---|---|
| follow | $988.12 | -1.19% | 3 | 4 | 1 | $-9.34 | $0.00 |
| priceaction | $1,000.00 | +0.00% | 0 | 0 | 0 | $+0.00 | $0.00 |
| trend | $992.63 | -0.74% | 0 | 2 | 0 | $-7.37 | $0.00 |

### follow: open positions

| product | entry | stop | target | size | why |
|---|---|---|---|---|---|
| BTC-USD | 81,493.46 | 78,438.94 | 87,608.40 | $81 | 1/1 followed traders long, avg weight 13% |
| SOL-USD | 99.78 | 93.70 | 111.95 | $58 | 1/1 followed traders long, avg weight 9% |
| ETH-USD | 2,299.66 | 2,202.23 | 2,494.03 | $74 | 1/1 followed traders long, avg weight 17% |

### follow: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| ETH-USD | stop | $-5.10 | 1/1 followed traders long, avg weight 8% |
| BTC-USD | timeout | $+0.43 | 1/1 followed traders long, avg weight 12% |
| ETH-USD | timeout | $-2.68 | 1/1 followed traders long, avg weight 10% |
| SOL-USD | timeout | $-1.99 | 1/1 followed traders long, avg weight 6% |

### priceaction: chart read (6h structure, 1h trigger)

| product | price | 6h trend | support | resistance | 1h candle | setup / why not |
|---|---|---|---|---|---|---|
| BTC-USD | 81,074.82 | range | 80093.82 | 82104.0 | - | waiting for a bullish 1h candle at support |
| ETH-USD | 2,354.12 | range | 2361.945 | 2414.39 | bullish pin bar | target 2414.3900 pays 0.16% vs risk 2.77% after 2.4% fees; need 2:1 |
| SOL-USD | 101.90 | down | 95.35 | 102.76 | - | downtrend: no longs |
| PAXG-USD | 4,034.27 | range | 4034.1 | 4151.17 | - | waiting for a bullish 1h candle at support |

### trend: last closed trades

| product | result | P&L | why it was taken |
|---|---|---|---|
| BTC-USD | timeout | $-4.64 | above rising 50d SMA (81541.56), pullback entry |
| BTC-USD | timeout | $-2.73 | above rising 50d SMA (81023.76), pullback entry |
