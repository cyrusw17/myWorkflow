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

**Quarterly stock-type selection (replaces fixed tech floor):**
1. On each calendar quarter open, classify market regime from SPY trend + vol stress:
   - `risk_on` — uptrend, calm vol → prefer tech / consumer / financials
   - `recovery` — vol stress but stabilizing uptrend → financials / industrials / consumer
   - `late_cycle` — warm trend with rising vol → energy / financials / industrials
   - `risk_off` — downtrend or high stress → defensive / health / staples
2. Score sleeves by relative strength vs SPY (~63d) and keep the top ~3 for that quarter
3. Run residual-momentum **only inside the active sleeves** for the quarter

**Activity:** weekly rebalance of top residual-momentum names inside the active sleeves.

A *trade* is an entry (weight 0 → >0).

**Research shadow book:** long top / short bottom; beta-neutralize portfolio to SPY.

### Risk
- Max weight per name: equal-weight ≈ 12.5% at `n_hold=8`
- Sleeve set is re-chosen quarterly; names outside the new sleeve are rotated out first
- No leverage > 1.0 in Phase 0 retail book

## Benchmark
Must beat **SPY buy-and-hold** and **vol-matched SPY** after costs on walk-forward.

## Primary failure modes
1. Residual ≈ raw momentum (no incremental edge)
2. Residual book is closet SPY with turnover tax
3. Crowding / capacity in microcaps that fail liquidity gates

## Status
Spec locked for Phase 0 bake-off.
