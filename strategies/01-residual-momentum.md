# Strategy 1 — Residual Momentum

## Thesis
Raw price momentum is often equity beta wearing a costume. Residual momentum trades **continuation in idiosyncratic returns** after removing market (and optionally style) exposure.

## Intuition (one line)
Names that keep beating what SPY says they “should” return continue to do so for a persistence window.

## Signal construction

### Universe
- US listed stocks / ETFs
- Liquidity gates (defaults — ablate): price ≥ $5, 20d ADV ≥ $25M, listed on NYSE/NASDAQ
- Exclude the strategy funding vehicle if needed; SPY is the factor/benchmark

### Residualization
For each name \(i\) on day \(t\), over lookback \(L \in \{60, 90, 126\}\):

\[
r_{i,\tau} = \alpha_i + \beta_i\, r_{\mathrm{SPY},\tau} + \varepsilon_{i,\tau}
\]

Residual momentum score \(S_{i,t}\):

\[
S_{i,t} = \sum_{\tau = t-W-G}^{t-G} \hat\varepsilon_{i,\tau}
\]

- Formation window \(W \in \{21, 63, 126\}\)
- Skip/gap \(G \in \{0, 1, 5\}\) trading days (classic momentum lag ablation)

### Portfolio
**Retail default (Robinhood-realistic):** long-only equal-weight sleeve of `n_hold` names (default 8).

**Activity targets (Phase 0 ops):**
- **~20 trades/month** — daily rebalance with ~1 new entry per rebalance day
- **≥30% of trades in technology** — tech sleeve (`XLK`/`QQQ` + megacap/semicap software/semis); entry bias + holding floor enforce the share

A *trade* is an entry (weight 0 → >0).

**Research shadow book:** long top / short bottom; beta-neutralize portfolio to SPY.

### Risk
- Max weight per name: equal-weight ≈ 12.5% at `n_hold=8` (soft vs classic 5–10% — prefer more names over concentration when expanding)
- Technology trade floor: ≥30% of entries
- No leverage > 1.0 in Phase 0 retail book

## Benchmark
Must beat **SPY buy-and-hold** and **vol-matched SPY** after costs on walk-forward.

## Primary failure modes
1. Residual ≈ raw momentum (no incremental edge)
2. Residual book is closet SPY with turnover tax
3. Crowding / capacity in microcaps that fail liquidity gates

## Status
Spec locked for Phase 0 bake-off.
