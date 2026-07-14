# DECISION_MEMO

> Interim fill from first automated bake-off. Replace after nested walk-forward.

**Date:** 2026-07-14  
**Data range:** 2018-01-01 → present (Yahoo daily OHLC)  
**Winner:** `SHIP_A_PAPER` (interim — A barely clears SPY vol-match Sharpe; **not** walk-forward validated)

## Metrics table

| Metric | SPY B&H | SPY vol-match | Strat A Residual Mom | Strat B LSC proxy |
|--------|---------|---------------|----------------------|-------------------|
| Sharpe | ~0.72 | ~0.65 | ~0.73 | ~-0.50 |
| CAGR | ~12.8% | ~10.0% | ~10.7% | ~-6.7% |
| Max DD | ~-34% | ~-26% | ~-22% | ~-50% |

See live numbers on GitHub Pages (`site/data/bakeoff.json`).

## Why winner vs SPY
- A edges vol-matched SPY on Sharpe with lower max DD than B&H in this first cut.
- Margin is thin — treat as provisional until walk-forward.

## Why loser failed
- Daily LSC proxy has negative expectancy / Sharpe after costs.
- Full 5m confluence engine not implemented yet; do not revive B without that stack + WF.

## Robinhood implementation risk
- A (weekly-ish rebalance ETFs) is simpler on RH than intraday LSC (PDT, fills).

## Next action
Run nested walk-forward on A; keep B as research until 1H/5m state machine is coded.
