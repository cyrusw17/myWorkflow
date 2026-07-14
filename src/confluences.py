"""
Confluence overlays on residual-momentum — long-only, drawdown-first.

Each confluence modulates exposure to a base residual-momentum return stream.
Designed for retail survivability (Robinhood-feasible equities, no shorts).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.metrics import equity_from_returns


@dataclass(frozen=True)
class Confluence:
    id: str
    name: str
    thesis: str
    apply: Callable[[pd.Series, pd.DataFrame], pd.Series]


def _clip01(x: pd.Series) -> pd.Series:
    return x.clip(lower=0.0, upper=1.0).fillna(0.0)


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=max(5, n // 3)).mean()


def _ann_vol(rets: pd.Series, n: int = 21) -> pd.Series:
    return rets.rolling(n, min_periods=max(5, n // 2)).std() * np.sqrt(252)


def _rsi(prices: pd.Series, n: int = 14) -> pd.Series:
    delta = prices.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    au = up.rolling(n, min_periods=n).mean()
    ad = down.rolling(n, min_periods=n).mean()
    rs = au / ad.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def _exposure_scale(base: pd.Series, exposure: pd.Series) -> pd.Series:
    """Apply lagged exposure so we don't peek."""
    exp = _clip01(exposure.shift(1)).fillna(0.0)
    out = (base * exp).rename(base.name)
    return out


def _vol_target(base: pd.Series, target: float, lookback: int = 63, cap: float = 1.0) -> pd.Series:
    rolling = _ann_vol(base, lookback).replace(0, np.nan)
    lever = (target / rolling).clip(upper=cap).shift(1).fillna(0.0)
    return (base * lever).rename(base.name)


def survival_score(metrics: dict, hard_max_dd: float = 0.35) -> float:
    """
    Account-survival rank for retail capital.
    Hard-rejects pathways that historically drew down past hard_max_dd.
    Otherwise emphasizes Calmar + Sortino, with early DD penalties.
    """
    mdd = abs(float(metrics.get("max_dd") or 0.0))
    if mdd > hard_max_dd + 1e-12:
        return -1000.0 - mdd  # keep ordering among rejects
    sharpe = float(metrics.get("sharpe") or 0.0)
    sortino = float(metrics.get("sortino") or 0.0)
    calmar = float(metrics.get("calmar") or 0.0)
    cagr = float(metrics.get("cagr") or 0.0)
    # Prefer strategies that still compound after DD is controlled.
    dd_pen = 1.0 / (1.0 + max(mdd - 0.12, 0.0) * 4.0)
    raw = 0.40 * calmar + 0.30 * sortino + 0.20 * sharpe + 0.10 * max(cagr, 0.0) * 5.0
    return float(raw * dd_pen)


def _build_catalog() -> list[Confluence]:
    def c01_spy_200(base, prices):
        spy = prices["SPY"]
        gate = (spy > _sma(spy, 200)).astype(float)
        return _exposure_scale(base, gate)

    def c02_vol_calm(base, prices):
        spy_rets = prices["SPY"].pct_change()
        vol = _ann_vol(spy_rets, 21)
        med = vol.rolling(252, min_periods=60).median()
        gate = (vol <= med).astype(float)
        return _exposure_scale(base, gate)

    def c03_crash_hedge(base, prices):
        spy = prices["SPY"]
        ret20 = spy / spy.shift(20) - 1.0
        # Full size normally; cut to 25% after sharp SPY air-pockets.
        exp = pd.Series(1.0, index=prices.index)
        exp = exp.where(ret20 > -0.08, 0.25)
        return _exposure_scale(base, exp)

    def c04_underwater_delever(base, prices):
        eq = equity_from_returns(base)
        dd = eq / eq.cummax() - 1.0
        exp = pd.Series(1.0, index=base.index)
        exp = exp.where(dd > -0.08, 0.5)
        exp = exp.where(dd > -0.15, 0.15)
        return _exposure_scale(base, exp)

    def c05_vol_target_12(base, prices):
        return _vol_target(base, target=0.12, cap=1.0)

    def c06_vol_target_10(base, prices):
        return _vol_target(base, target=0.10, cap=1.0)

    def c07_dual_momentum(base, prices):
        spy = prices["SPY"]
        abs_mom = spy / spy.shift(126) - 1.0
        gate = (abs_mom > 0).astype(float)
        return _exposure_scale(base, gate)

    def c08_tech_rs(base, prices):
        if "XLK" not in prices.columns:
            return base
        rs = prices["XLK"] / prices["SPY"]
        gate = (rs > _sma(rs, 63)).astype(float)
        # Soft: 50% size when tech RS is weak
        exp = gate.where(gate > 0, 0.5)
        return _exposure_scale(base, exp)

    def c09_defensive_blend(base, prices):
        spy = prices["SPY"]
        peak = spy.cummax()
        spy_dd = spy / peak - 1.0
        defs = [c for c in ("XLU", "XLP", "GLD", "TLT") if c in prices.columns]
        if not defs:
            return _exposure_scale(base, (spy_dd > -0.10).astype(float))
        def_rets = prices[defs].pct_change().mean(axis=1).fillna(0.0)
        # When SPY is in >10% drawdown, replace half of residual book with defensives.
        stress = (spy_dd <= -0.10).astype(float).shift(1).fillna(0.0)
        mixed = base * (1.0 - 0.5 * stress) + def_rets * (0.5 * stress)
        return mixed.rename(base.name)

    def c10_score_persistence(base, prices):
        # Proxy: require strategy's own 21d momentum positive.
        mom = equity_from_returns(base)
        gate = (mom > mom.shift(21)).astype(float)
        exp = gate.where(gate > 0, 0.35)
        return _exposure_scale(base, exp)

    def c11_breadth(base, prices):
        names = prices.drop(columns=["SPY"], errors="ignore")
        # Share of names beating SPY over 21d.
        spy21 = prices["SPY"] / prices["SPY"].shift(21) - 1.0
        rel = names / names.shift(21) - 1.0
        breadth = (rel.gt(spy21, axis=0)).mean(axis=1)
        gate = (breadth >= 0.45).astype(float)
        exp = gate.where(gate > 0, 0.25)
        return _exposure_scale(base, exp)

    def c12_corr_regime(base, prices):
        # High average correlation → cut risk (crowded beta).
        rets = prices[["SPY", "QQQ", "IWM", "XLF", "XLE", "XLV", "XLK"]].pct_change()
        rets = rets.dropna(how="all")
        # Rolling pairwise corr mean via variance of equal-weight vs singles (approx).
        ew = rets.mean(axis=1)
        # Use 63d corr of QQQ vs SPY + IWM vs SPY as crowding proxy.
        c1 = rets["QQQ"].rolling(63).corr(rets["SPY"])
        c2 = rets["IWM"].rolling(63).corr(rets["SPY"])
        crowd = ((c1 + c2) / 2.0).reindex(base.index)
        exp = pd.Series(1.0, index=base.index)
        exp = exp.where(crowd < 0.85, 0.4)
        exp = exp.where(crowd < 0.92, 0.15)
        return _exposure_scale(base, exp)

    def c13_rsi_cooloff(base, prices):
        rsi = _rsi(prices["SPY"], 14)
        exp = pd.Series(1.0, index=prices.index)
        exp = exp.where(rsi < 75, 0.35)
        exp = exp.where(rsi < 80, 0.0)
        return _exposure_scale(base, exp)

    def c14_gap_filter(base, prices):
        # Avoid initiating risk after violent overnight gap days (SPY open proxy via large 1d move).
        move = prices["SPY"].pct_change().abs()
        exp = pd.Series(1.0, index=prices.index)
        exp = exp.where(move < 0.025, 0.25)
        return _exposure_scale(base, exp)

    def c15_circuit_breaker(base, prices):
        eq = equity_from_returns(base)
        peak = eq.cummax()
        dd = eq / peak - 1.0
        # Flatten until strategy makes a new equity high after -15% breach.
        flat = False
        exp_vals = []
        for i, (dt, ddv) in enumerate(dd.items()):
            if ddv <= -0.15:
                flat = True
            if flat and eq.iloc[i] >= peak.iloc[i] - 1e-12 and ddv > -1e-12:
                flat = False
            # During flatten, exposure 0; otherwise 1. Peak equality only at new highs.
            if flat:
                # Stay flat until recover to within 2% of running peak after breach.
                if eq.iloc[i] / peak.iloc[i] >= 0.98:
                    flat = False
                    exp_vals.append(1.0)
                else:
                    exp_vals.append(0.0)
            else:
                exp_vals.append(1.0)
        exp = pd.Series(exp_vals, index=dd.index)
        return _exposure_scale(base, exp)

    def c16_half_vol_scale(base, prices):
        # Target half of trailing strategy vol (delever naturally).
        vol = _ann_vol(base, 63).replace(0, np.nan)
        target = (0.5 * vol).clip(lower=0.06, upper=0.12)
        lever = (target / vol).clip(upper=1.0).shift(1).fillna(0.0)
        return (base * lever).rename(base.name)

    def c17_golden_cross(base, prices):
        spy = prices["SPY"]
        s50 = _sma(spy, 50)
        s200 = _sma(spy, 200)
        gate = ((spy > s50) & (s50 > s200)).astype(float)
        return _exposure_scale(base, gate)

    def c18_bond_stress(base, prices):
        if "TLT" not in prices.columns:
            return base
        tlt = prices["TLT"]
        ret15 = tlt / tlt.shift(15) - 1.0
        # Bond dump often = liquidity stress for risk assets.
        exp = pd.Series(1.0, index=prices.index)
        exp = exp.where(ret15 > -0.06, 0.35)
        return _exposure_scale(base, exp)

    def c19_dispersion(base, prices):
        # Trade full size when cross-sectional dispersion is healthy (edge exists).
        rets = prices.drop(columns=["SPY"], errors="ignore").pct_change()
        disp = rets.rolling(21).std().mean(axis=1)
        med = disp.rolling(252, min_periods=60).median()
        gate = (disp >= 0.85 * med).astype(float)
        exp = gate.where(gate > 0, 0.3)
        return _exposure_scale(base, exp)

    def c20_smooth_exposure(base, prices):
        # 5-day smoothed version of a conservative trend gate — reduces whipsaw liquidation risk.
        spy = prices["SPY"]
        gate = (spy > _sma(spy, 100)).astype(float)
        smooth = gate.rolling(5, min_periods=1).mean()
        return _exposure_scale(base, smooth)

    return [
        Confluence("c01_spy_200", "SPY > 200dma gate", "Risk-on only when SPY is in a long uptrend.", c01_spy_200),
        Confluence("c02_vol_calm", "Calm-vol only", "Stand down when realized SPY vol is above its year median.", c02_vol_calm),
        Confluence("c03_crash_hedge", "Crash air-pocket cut", "Cut to 25% risk after SPY −8% in 20d.", c03_crash_hedge),
        Confluence("c04_underwater_delever", "Underwater delever", "Delever the book as its own drawdown deepens.", c04_underwater_delever),
        Confluence("c05_vol_target_12", "Vol-target 12%", "Cap strategy risk at ~12% annualized vol.", c05_vol_target_12),
        Confluence("c06_vol_target_10", "Vol-target 10%", "More conservative ~10% vol targeting.", c06_vol_target_10),
        Confluence("c07_dual_momentum", "Dual momentum (abs)", "Require positive 126d SPY absolute momentum.", c07_dual_momentum),
        Confluence("c08_tech_rs", "Tech RS confirm", "Full size only when XLK relative strength is healthy.", c08_tech_rs),
        Confluence("c09_defensive_blend", "Defensive blend", "In SPY drawdowns, blend toward utilities/staples/gold/bonds.", c09_defensive_blend),
        Confluence("c10_persist", "Own-trend persistence", "Require the strategy equity itself to be rising over 21d.", c10_score_persistence),
        Confluence("c11_breadth", "Market breadth", "Require enough names beating SPY (opportunity set).", c11_breadth),
        Confluence("c12_corr_regime", "Anti-crowd corr", "Cut risk when QQQ/IWM become ultra-correlated to SPY.", c12_corr_regime),
        Confluence("c13_rsi_cooloff", "RSI cool-off", "Fade exposure when SPY RSI is euphoric.", c13_rsi_cooloff),
        Confluence("c14_gap_filter", "Gap/shock filter", "Cut risk after violent 1-day SPY shocks.", c14_gap_filter),
        Confluence("c15_circuit_breaker", "−15% circuit breaker", "Go flat after −15% strategy DD until near recovery.", c15_circuit_breaker),
        Confluence("c16_half_vol", "Half-vol scale", "Always run around half trailing strategy vol.", c16_half_vol_scale),
        Confluence("c17_golden_cross", "Golden-cross stack", "SPY above 50dma and 50 above 200.", c17_golden_cross),
        Confluence("c18_bond_stress", "Bond-stress cut", "Cut equity risk when TLT dumps (liquidity stress).", c18_bond_stress),
        Confluence("c19_dispersion", "Dispersion regime", "Full size when cross-sectional dispersion supports stock picking.", c19_dispersion),
        Confluence("c20_smooth_trend", "Smoothed trend gate", "100dma gate with 5d exposure smoothing.", c20_smooth_exposure),
    ]


CONFLUENCES: list[Confluence] = _build_catalog()


def apply_confluence(confluence_id: str, base_rets: pd.Series, prices: pd.DataFrame) -> pd.Series:
    for c in CONFLUENCES:
        if c.id == confluence_id:
            out = c.apply(base_rets, prices)
            return out.reindex(base_rets.index).fillna(0.0)
    raise KeyError(f"Unknown confluence: {confluence_id}")


def catalog_meta() -> list[dict]:
    return [{"id": c.id, "name": c.name, "thesis": c.thesis} for c in CONFLUENCES]
