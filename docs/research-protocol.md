# Research Protocol — Strategy Bake-Off vs SPY

## Purpose
Decide whether Residual Momentum (A), Liquidity Sweep Continuation (B), both, or neither deserve paper capital — relative to SPY baselines.

## Pre-commit (no moving goalposts mid-test)

### Cost model (defaults)
- Equities/ETFs commission: $0
- Slippage: max(half-spread estimate, 1 bp) per side for liquid ETFs; scale up for single names by ADV
- Strategy B: assume conservative 5m fill = signal bar close ± 1 bp (ablate 2–5 bp)

### Capital & constraints
- Starting capital: configurable (default $25,000 to reflect PDT-aware day trading)
- No infinite leverage
- Strategy B: track pattern-day-trade count

### Walk-forward
- Anchored or rolling folds with ≥ 1 year OOS chunks when history allows
- Param selection **only** inside training folds
- Report median and IQR of OOS Sharpe

## Metrics (required)
CAGR/total return, vol, Sharpe, Sortino, max DD, Calmar, turnover, correlation to SPY, worst month, net after costs.

Strategy B extras: profit factor, expectancy (R), win rate, trade count, max losing streak, % sessions traded.

## Decision rule (lexicographic)
1. Kill criteria cleared?
2. Higher median OOS Sharpe vs relevant SPY baseline
3. Lower max DD
4. Lower Robinhood implementation risk
5. Else `KILL_REDESIGN`

## Decision memo template

```markdown
# DECISION_MEMO

Date:
Data range:
Winner: SHIP_A_PAPER | SHIP_B_PAPER | SHIP_ENSEMBLE_PAPER | KILL_REDESIGN

## Metrics table
(paste)

## Why winner vs SPY
(3 bullets max)

## Why loser failed
(3 bullets max)

## Implementation risk on Robinhood
(A vs B)

## Next action
(one concrete action)
```

## Reproducibility
One CLI entrypoint must regenerate metrics from raw inputs. Notebooks are optional; they are not the source of truth.
