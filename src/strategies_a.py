from __future__ import annotations

import numpy as np
import pandas as pd


def residual_momentum_returns(
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    lookback_beta: int = 90,
    formation: int = 63,
    skip: int = 1,
    top_quantile: float = 0.2,
    rebalance_every: int = 5,
    cost_bps: float = 5.0,
) -> pd.Series:
    """
    Long-only top residual-momentum quantile, equal-weight, periodic rebalance.
    Residual via trailing regression vs SPY on daily log returns.
    """
    cols = [c for c in prices.columns if c != spy_col]
    rets = np.log(prices / prices.shift(1))
    spy = rets[spy_col]

    # Rolling beta and residual approx: eps = r - beta * spy (alpha folded into residual momentum sum)
    betas = pd.DataFrame(index=rets.index, columns=cols, dtype=float)
    for c in cols:
        cov = rets[c].rolling(lookback_beta).cov(spy)
        var = spy.rolling(lookback_beta).var()
        betas[c] = cov / var.replace(0, np.nan)

    resid = rets[cols] - betas.mul(spy, axis=0)
    # Formation sum of residuals, skipping most recent `skip` days
    score = resid.shift(skip).rolling(formation).sum()

    port = pd.Series(0.0, index=prices.index, name="residual_momentum")
    weights = pd.Series(0.0, index=cols)
    cost = cost_bps / 10000.0

    for i, dt in enumerate(prices.index):
        if i < lookback_beta + formation + skip + 1:
            continue
        if i % rebalance_every == 0:
            s = score.loc[dt].dropna()
            if len(s) < 3:
                continue
            n_top = max(1, int(np.ceil(len(s) * top_quantile)))
            top = s.nlargest(n_top).index.tolist()
            new_w = pd.Series(0.0, index=cols)
            new_w.loc[top] = 1.0 / len(top)
            turnover = (new_w - weights).abs().sum() / 2.0
            day_ret = float((rets.loc[dt, cols].fillna(0.0) * new_w).sum()) - turnover * cost
            weights = new_w
            port.loc[dt] = day_ret
        else:
            day_ret = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            port.loc[dt] = day_ret

    return port.fillna(0.0)
