# Strategy 2 — Liquidity Sweep Continuation (LSC)

## Thesis
Intraday continuation after a **stop-run / liquidity sweep** of a meaningful high/low, only when multi-factor confluence confirms that the sweep was manipulation rather than a clean breakout — then trade the reclaim/continuation on the execution timeframe.

## Style
Day trading / intraday. Prefer flat by RTH close unless a tested overnight rule is later approved.

## Human rules (intent)
1. Liquidity Sweep (1H, 4H, session high/lows)
2. 5 confirmation confluence: BOS, IFVG, SMT, 79% extension (+ locked 5th — default **displacement**)
3. If sweep happens in premarket or a different session → wait for **5-minute manipulation**
4. 5m continuation confirmation: EQ or FVG; if (3) fired → require **SMT divergence**

## State machine

```
IDLE
  → SWEPT            (valid sweep event tagged with TF + session)
  → WAIT_MANIP       (only if sweep session ≠ execution session OR premarket)
  → CONFLUENCE       (score confirmations)
  → ARMED            (score + path rules pass)
  → IN_TRADE
  → FLAT             (target / stop / time-stop)
```

Illegal transitions must be logged and rejected.

## Operational definitions (defaults — freeze before backtest)

| Term | Default measurable rule |
|------|-------------------------|
| RTH | 09:30–16:00 America/New_York |
| Premarket | 04:00–09:30 ET |
| Session high/low | Prior RTH high/low as primary liquidity pool; developing session optional v2 |
| Sweep | Trade beyond pool extreme by ≥ 0.05% (ETFs) or 1× tick buffer, then close back inside within 3 candles on detection TF |
| Detection TFs | 4H and 1H primary; session H/L always watched |
| BOS | Close beyond last opposite swing high/low on 5m or 15m (choose one; default 5m) |
| FVG | 3-candle gap: candle1 high < candle3 low (bull) or candle1 low > candle3 high (bear) |
| IFVG | Prior FVG inverted (price closes through), then later respected as support/resistance |
| SMT | SPY vs QQQ (or sector peer): price makes new sweep extreme while peer does not (divergence) within window |
| 79% ext | Fib extension 0.79 of impulse leg that caused the sweep reclaim; touch within tolerance |
| Displacement | Impulsive candle (≥ 1.2× ATR(14) on TF) in reclaim direction closing near extreme |
| 5m manipulation | After off-session sweep, 5m sweep of a local EQ/prior high-low that fails within 6 bars |
| EQ | Highs/lows within 0.02% (ETF) tolerance, ≥ 2 touches |
| Entry | Next mid/ask on ARMED close; or limit at FVG midline (ablate) |
| Stop | Beyond swept extreme + 0.05% buffer |
| Target | 1.5R fixed + opposing session liquidity partial; full flat by 15:55 ET |
| Size | Risk 0.5% equity to stop |

## Confluence score (5 slots)
1. BOS  
2. IFVG  
3. SMT  
4. 79% extension  
5. Displacement  

**Base path (in-session sweep):** need \(C \ge 4\) with BOS mandatory.  
**Off-session / premarket path:** WAIT_MANIP must succeed → then EQ or FVG continuation, and **SMT mandatory**.

## SPY comparison (correct baseline)
Do **not** only compare to buy-and-hold SPY. Also compare daily PnL Sharpe to:
- Hold SPY only during RTH
- Cash overnight

Ask: are we generating **idiosyncratic intraday edge** or dressed-up beta?

## Kill criteria
- Cannot automate without discretion
- Edge dies with realistic spreads/slippage on 5m bars
- PnL concentrated in tiny trade count
- OOS daily Sharpe ≤ 0

## Status
Spec locked for Phase 0 bake-off — numerics are defaults for ablation, not holy writ.
