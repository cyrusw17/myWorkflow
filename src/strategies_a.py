from __future__ import annotations

import numpy as np
import pandas as pd

TECH_TICKERS = {
    "XLK",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AVGO",
    "AMD",
    "CRM",
    "ORCL",
    "ADBE",
    "CSCO",
    "INTC",
    "TXN",
    "QCOM",
    "AMAT",
    "META",
    "GOOGL",
    "AMZN",
    "MU",
    "NOW",
}


def _ranked(score_row: pd.Series) -> list[str]:
    return score_row.sort_values(ascending=False).index.tolist()


def residual_momentum_returns(
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    lookback_beta: int = 90,
    formation: int = 63,
    skip: int = 1,
    n_tech: int = 4,
    n_other: int = 4,
    tech_weight: float = 0.50,
    rebalance_every: int = 5,
    cost_bps: float = 5.0,
    tech_tickers: set[str] | None = None,
) -> tuple[pd.Series, dict]:
    """
    Long-only residual momentum with a fixed technology portfolio weight.

    Each rebalance:
      - rank residual-momentum scores for tech and non-tech sleeves
      - hold top `n_tech` tech + top `n_other` non-tech
      - assign total weight `tech_weight` evenly across tech names,
        and `1 - tech_weight` evenly across non-tech names
    """
    tech = set(tech_tickers or TECH_TICKERS)
    tech_weight = float(np.clip(tech_weight, 0.0, 1.0))
    other_weight = 1.0 - tech_weight

    cols = [c for c in prices.columns if c != spy_col]
    tech_cols = [c for c in cols if c in tech]
    other_cols = [c for c in cols if c not in tech]
    if not tech_cols:
        raise ValueError("Universe has no technology tickers")
    if tech_weight < 1.0 and not other_cols:
        raise ValueError("Universe has no non-tech tickers for leftover weight")

    rets = np.log(prices / prices.shift(1))
    spy = rets[spy_col]

    betas = pd.DataFrame(index=rets.index, columns=cols, dtype=float)
    for c in cols:
        cov = rets[c].rolling(lookback_beta).cov(spy)
        var = spy.rolling(lookback_beta).var()
        betas[c] = cov / var.replace(0, np.nan)

    resid = rets[cols] - betas.mul(spy, axis=0)
    score = resid.shift(skip).rolling(formation).sum()

    port = pd.Series(0.0, index=prices.index, name="residual_momentum")
    weights = pd.Series(0.0, index=cols)
    cost = cost_bps / 10000.0
    trade_log: list[dict] = []
    warmup = lookback_beta + formation + skip + 1
    last_reb = -10**9

    for i, dt in enumerate(prices.index):
        if i < warmup:
            continue

        if (i - last_reb) < rebalance_every:
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            continue

        s = score.loc[dt].dropna()
        tech_ranked = [t for t in _ranked(s) if t in tech_cols]
        other_ranked = [t for t in _ranked(s) if t in other_cols]

        pick_tech = tech_ranked[: min(n_tech, len(tech_ranked))]
        pick_other = other_ranked[: min(n_other, len(other_ranked))] if other_weight > 1e-12 else []

        # If a sleeve is empty, spill remaining weight into the other sleeve.
        new_w = pd.Series(0.0, index=cols)
        if pick_tech and tech_weight > 1e-12:
            w = tech_weight if pick_other else 1.0
            new_w.loc[pick_tech] = w / len(pick_tech)
        if pick_other and other_weight > 1e-12:
            w = other_weight if pick_tech else 1.0
            new_w.loc[pick_other] = w / len(pick_other)
        if new_w.sum() <= 0:
            port.loc[dt] = 0.0
            continue

        # Normalize in case of float noise.
        new_w = new_w / new_w.sum()

        for t in new_w[new_w > 0].index:
            if float(weights.get(t, 0.0)) <= 0:
                trade_log.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "ticker": t,
                        "is_tech": t in tech,
                    }
                )

        turnover = (new_w - weights).abs().sum() / 2.0
        port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * new_w).sum()) - turnover * cost
        weights = new_w
        last_reb = i

    port = port.fillna(0.0)
    live = port.iloc[warmup:]
    years = max((live.index[-1] - live.index[0]).days / 365.25, 1e-9) if len(live) > 1 else 1e-9
    months = years * 12.0
    n_trades = len(trade_log)
    n_tech_trades = sum(1 for t in trade_log if t["is_tech"])
    stats = {
        "mode": "tech_weight_residual_momentum",
        "tech_weight": tech_weight,
        "n_tech": n_tech,
        "n_other": n_other,
        "rebalance_every": rebalance_every,
        "n_trades": n_trades,
        "trades_per_month": (n_trades / months) if months > 0 else 0.0,
        "tech_trade_share": (n_tech_trades / n_trades) if n_trades else 0.0,
        "tech_universe": sorted(tech_cols),
    }
    return port, stats


def drawdown_aware_score(metrics: dict) -> float:
    """
    Rank score that rewards return quality while punishing drawdowns.
    Uses Calmar as primary signal, blended with Sharpe.
    """
    sharpe = float(metrics.get("sharpe") or 0.0)
    calmar = float(metrics.get("calmar") or 0.0)
    mdd = abs(float(metrics.get("max_dd") or 0.0))
    # Soft penalty if drawdown is catastrophic even when Calmar is noisy.
    dd_penalty = 1.0 / (1.0 + max(mdd - 0.25, 0.0) * 2.0)
    return (0.55 * calmar + 0.45 * sharpe) * dd_penalty
