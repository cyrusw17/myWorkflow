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
**Retail default (Robinhood-realistic):** long-only equal-weight within sleeves.

**Technology weight (Phase 0):**
- Split the book into a **tech sleeve** and a **non-tech sleeve**
- Hold top residual-score tech names + top residual-score diversifiers
- Assign a fixed portfolio weight \(w_{\mathrm{tech}} \in [0.25, 0.95]\) to the tech sleeve (swept in research); remainder to non-tech
- Weekly rebalance

**Research selection rule:** pick \(w_{\mathrm{tech}}\) by drawdown-aware score  
`0.55 * Calmar + 0.45 * Sharpe` (soft penalty if `|maxDD| > 25%`).

### Risk
- Tech concentration is an explicit dial, not an accidental factor bet
- No leverage > 1.0 in Phase 0 retail book

## Benchmark
Must beat **SPY buy-and-hold** and **vol-matched SPY** after costs on walk-forward.

## Primary failure modes
1. Residual ≈ raw momentum (no incremental edge)
2. Residual book is closet SPY with turnover tax
3. Crowding / capacity in microcaps that fail liquidity gates
4. Tech weight too high → path-dependent tech drawdowns dominate

## Status
Spec locked for Phase 0 bake-off (tech-weight sweep).
