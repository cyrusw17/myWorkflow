from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Stock-type sleeves. Residual momentum only picks inside the active quarterly set.
SECTOR_MAP: dict[str, str] = {
    # Technology / growth
    "XLK": "tech",
    "QQQ": "tech",
    "AAPL": "tech",
    "MSFT": "tech",
    "NVDA": "tech",
    "AVGO": "tech",
    "AMD": "tech",
    "CRM": "tech",
    "ORCL": "tech",
    "ADBE": "tech",
    "CSCO": "tech",
    "INTC": "tech",
    "TXN": "tech",
    "QCOM": "tech",
    "AMAT": "tech",
    "META": "tech",
    "GOOGL": "tech",
    "MU": "tech",
    "NOW": "tech",
    # Consumer
    "AMZN": "consumer",
    "XLY": "consumer",
    "XLP": "consumer",
    "WMT": "consumer",
    "PG": "consumer",
    "KO": "consumer",
    "HD": "consumer",
    "DIS": "consumer",
    # Financials
    "XLF": "financials",
    "JPM": "financials",
    "BAC": "financials",
    "V": "financials",
    "MA": "financials",
    # Energy
    "XLE": "energy",
    "XOM": "energy",
    # Health
    "XLV": "health",
    "JNJ": "health",
    "UNH": "health",
    # Industrials
    "XLI": "industrials",
    "CAT": "industrials",
    "BA": "industrials",
    "IWM": "industrials",
    # Defensive / alternative
    "XLU": "defensive",
    "GLD": "defensive",
    "TLT": "defensive",
}

# Preferred sleeves by market regime (ordered). Relative strength then trims to n_sectors.
REGIME_PREF: dict[str, list[str]] = {
    "risk_on": ["tech", "consumer", "financials", "industrials", "energy"],
    "recovery": ["financials", "industrials", "consumer", "tech", "energy"],
    "late_cycle": ["energy", "financials", "industrials", "health", "consumer"],
    "risk_off": ["defensive", "health", "consumer", "tech", "financials"],
}


@dataclass
class RegimeDecision:
    date: str
    regime: str
    sectors: list[str]
    spy_ret_63: float
    spy_vol_21: float
    vol_ratio: float
    notes: str


def _quarter_key(dt: pd.Timestamp) -> tuple[int, int]:
    return int(dt.year), int((dt.month - 1) // 3)


def _ranked_by_score(score_row: pd.Series) -> list[str]:
    return score_row.sort_values(ascending=False).index.tolist()


def _sector_relative_strength(
    prices: pd.DataFrame,
    spy: pd.Series,
    dt: pd.Timestamp,
    lookback: int = 63,
) -> dict[str, float]:
    """Mean relative return of each sleeve vs SPY over lookback (ETF proxies preferred)."""
    if dt not in prices.index:
        return {}
    loc = prices.index.get_loc(dt)
    if isinstance(loc, slice):
        loc = loc.start
    start = max(0, int(loc) - lookback)
    window = prices.iloc[start : int(loc) + 1]
    if len(window) < max(10, lookback // 3):
        return {}

    spy_ret = float(spy.loc[window.index[-1]] / spy.loc[window.index[0]] - 1.0)
    scores: dict[str, list[float]] = {}
    for ticker, sector in SECTOR_MAP.items():
        if ticker not in window.columns:
            continue
        weight = 2.0 if ticker.startswith("X") or ticker in {"QQQ", "IWM", "GLD", "TLT"} else 1.0
        asset_ret = float(window[ticker].iloc[-1] / window[ticker].iloc[0] - 1.0)
        scores.setdefault(sector, []).append((asset_ret - spy_ret) * weight)

    return {sec: float(np.mean(vals)) for sec, vals in scores.items() if vals}


def classify_regime(
    spy_prices: pd.Series,
    dt: pd.Timestamp,
    vol_lookback: int = 21,
    trend_lookback: int = 63,
    vol_baseline: int = 252,
) -> tuple[str, dict]:
    """Map market condition → regime label using SPY trend + vol stress."""
    if dt not in spy_prices.index:
        return "risk_on", {"spy_ret_63": 0.0, "spy_vol_21": 0.0, "vol_ratio": 1.0}

    loc = spy_prices.index.get_loc(dt)
    if isinstance(loc, slice):
        loc = loc.start
    i = int(loc)
    if i < trend_lookback + 5:
        return "risk_on", {"spy_ret_63": 0.0, "spy_vol_21": 0.0, "vol_ratio": 1.0}

    px = spy_prices.iloc[: i + 1]
    rets = px.pct_change()
    ret_63 = float(px.iloc[-1] / px.iloc[-trend_lookback] - 1.0)
    ret_126 = float(px.iloc[-1] / px.iloc[-min(126, len(px) - 1)] - 1.0) if len(px) > 30 else ret_63
    vol_21 = float(rets.iloc[-vol_lookback:].std() * np.sqrt(252))
    base = rets.iloc[-min(vol_baseline, len(rets)) :]
    vol_med = float(base.rolling(vol_lookback).std().median() * np.sqrt(252)) or vol_21
    vol_ratio = vol_21 / vol_med if vol_med > 1e-12 else 1.0

    stressed = vol_ratio >= 1.35
    uptrend = ret_63 > 0 and ret_126 > -0.02
    strong_up = ret_63 > 0.04 and ret_126 > 0
    downtrend = ret_63 < -0.03 or (ret_63 < 0 and ret_126 < -0.05)

    if stressed and downtrend:
        regime = "risk_off"
    elif stressed and uptrend:
        regime = "recovery"
    elif strong_up and not stressed:
        regime = "risk_on"
    elif downtrend:
        regime = "risk_off"
    elif uptrend and vol_ratio > 1.15:
        regime = "late_cycle"
    else:
        regime = "risk_on"

    return regime, {
        "spy_ret_63": ret_63,
        "spy_vol_21": vol_21,
        "vol_ratio": vol_ratio,
    }


def pick_sectors_for_regime(
    regime: str,
    rs_scores: dict[str, float],
    n_sectors: int = 3,
) -> list[str]:
    pref = REGIME_PREF.get(regime, REGIME_PREF["risk_on"])
    available = [s for s in pref if s in rs_scores] or list(rs_scores.keys())
    if not available:
        return pref[:n_sectors]

    ranked = sorted(
        available,
        key=lambda s: (rs_scores.get(s, -1e9), -pref.index(s) if s in pref else -99),
        reverse=True,
    )
    chosen: list[str] = []
    if pref[0] in available:
        chosen.append(pref[0])
    for s in ranked:
        if s not in chosen:
            chosen.append(s)
        if len(chosen) >= n_sectors:
            break
    return chosen[:n_sectors]


def residual_momentum_returns(
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    lookback_beta: int = 90,
    formation: int = 63,
    skip: int = 1,
    n_hold: int = 8,
    rebalance_every: int = 5,
    n_sectors: int = 3,
    cost_bps: float = 5.0,
    sector_map: dict[str, str] | None = None,
) -> tuple[pd.Series, dict]:
    """
    Residual momentum with quarterly stock-type selection.

    Each calendar quarter:
      1) Classify market regime from SPY trend + vol stress
      2) Pick ~n_sectors stock types from regime prefs + relative strength
      3) Hold top residual-momentum names only inside that sleeve

    Weekly rebalance (default) rebuilds the equal-weight book from current scores.
    """
    sectors = dict(sector_map or SECTOR_MAP)
    cols = [c for c in prices.columns if c != spy_col and c in sectors]
    if len(cols) < n_hold:
        raise ValueError("Universe too small for residual momentum sleeve")

    rets = np.log(prices / prices.shift(1))
    spy = rets[spy_col]
    spy_px = prices[spy_col]

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
    regime_log: list[dict] = []
    active_sectors: list[str] = list(REGIME_PREF["risk_on"][:n_sectors])
    active_regime = "risk_on"
    current_quarter: tuple[int, int] | None = None
    warmup = lookback_beta + formation + skip + 1
    last_rebalance_i = -10**9

    for i, dt in enumerate(prices.index):
        if i < warmup:
            continue

        qk = _quarter_key(dt)
        quarter_turn = qk != current_quarter
        if quarter_turn:
            current_quarter = qk
            regime, meta = classify_regime(spy_px, dt)
            rs = _sector_relative_strength(prices[cols + [spy_col]], spy_px, dt)
            active_sectors = pick_sectors_for_regime(regime, rs, n_sectors=n_sectors)
            active_regime = regime
            regime_log.append(
                RegimeDecision(
                    date=dt.strftime("%Y-%m-%d"),
                    regime=regime,
                    sectors=list(active_sectors),
                    spy_ret_63=float(meta["spy_ret_63"]),
                    spy_vol_21=float(meta["spy_vol_21"]),
                    vol_ratio=float(meta["vol_ratio"]),
                    notes=f"RS top sleeves: {', '.join(active_sectors)}",
                ).__dict__
            )

        due = (i - last_rebalance_i) >= rebalance_every or quarter_turn
        if not due:
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            continue

        allowed = [c for c in cols if sectors.get(c) in active_sectors]
        s = score.loc[dt, allowed].dropna() if allowed else pd.Series(dtype=float)
        if len(s) < max(3, n_hold // 2):
            s = score.loc[dt].dropna()
        if len(s) < max(3, n_hold // 2):
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            continue

        ranked = _ranked_by_score(s)
        hold_n = max(4, n_hold - 2) if active_regime == "risk_off" else n_hold
        new_names = ranked[: min(hold_n, len(ranked))]

        new_w = pd.Series(0.0, index=cols)
        if new_names:
            new_w.loc[new_names] = 1.0 / len(new_names)

        for t in new_names:
            if float(weights.get(t, 0.0)) <= 0:
                trade_log.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "ticker": t,
                        "sector": sectors.get(t, "unknown"),
                        "regime": active_regime,
                    }
                )

        turnover = (new_w - weights).abs().sum() / 2.0
        port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * new_w).sum()) - turnover * cost
        weights = new_w
        last_rebalance_i = i

    port = port.fillna(0.0)
    live = port.iloc[warmup:]
    years = max((live.index[-1] - live.index[0]).days / 365.25, 1e-9) if len(live) > 1 else 1e-9
    months = years * 12.0
    n_trades = len(trade_log)
    sector_counts: dict[str, int] = {}
    for t in trade_log:
        sector_counts[t["sector"]] = sector_counts.get(t["sector"], 0) + 1

    stats = {
        "mode": "quarterly_regime_residual_momentum",
        "n_trades": n_trades,
        "trades_per_month": (n_trades / months) if months > 0 else 0.0,
        "n_hold": n_hold,
        "rebalance_every": rebalance_every,
        "n_sectors": n_sectors,
        "trade_sector_mix": {
            k: round(v / n_trades, 4)
            for k, v in sorted(sector_counts.items(), key=lambda kv: -kv[1])
        }
        if n_trades
        else {},
        "regime_decisions": regime_log,
        "latest_regime": regime_log[-1] if regime_log else None,
        "sector_map": {k: v for k, v in sectors.items() if k in cols},
    }
    return port, stats
