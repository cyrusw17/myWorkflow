from __future__ import annotations

import numpy as np
import pandas as pd


def equity_from_returns(rets: pd.Series, start_equity: float = 1.0) -> pd.Series:
    return (1.0 + rets.fillna(0.0)).cumprod() * start_equity


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min()) if len(dd) else 0.0


def ann_factor(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 252.0
    years = (index[-1] - index[0]).days / 365.25
    if years <= 0:
        return 252.0
    return len(index) / years


def summarize(rets: pd.Series, label: str) -> dict:
    rets = rets.dropna()
    if rets.empty:
        return {
            "name": label,
            "total_return": 0.0,
            "cagr": 0.0,
            "ann_vol": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "max_dd": 0.0,
            "calmar": 0.0,
            "hit_rate": 0.0,
        }
    eq = equity_from_returns(rets)
    af = ann_factor(rets.index)
    total = float(eq.iloc[-1] / eq.iloc[0] - 1.0)
    years = max((rets.index[-1] - rets.index[0]).days / 365.25, 1e-9)
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1.0)
    vol = float(rets.std() * np.sqrt(af))
    sharpe = float((rets.mean() * af) / vol) if vol > 1e-12 else 0.0
    downside = rets[rets < 0]
    dvol = float(downside.std() * np.sqrt(af)) if len(downside) else 0.0
    sortino = float((rets.mean() * af) / dvol) if dvol > 1e-12 else 0.0
    mdd = max_drawdown(eq)
    calmar = float(cagr / abs(mdd)) if abs(mdd) > 1e-12 else 0.0
    return {
        "name": label,
        "total_return": total,
        "cagr": cagr,
        "ann_vol": vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd": mdd,
        "calmar": calmar,
        "hit_rate": float((rets > 0).mean()),
    }


def vol_target_returns(asset_rets: pd.Series, target_vol: float, lookback: int = 63) -> pd.Series:
    """Scale asset returns to approximate target annual vol (for SPY vol-match)."""
    af = 252.0
    rolling = asset_rets.rolling(lookback).std() * np.sqrt(af)
    lever = (target_vol / rolling.replace(0, np.nan)).clip(upper=3.0).shift(1)
    return (asset_rets * lever.fillna(1.0)).rename("spy_vol_match")
