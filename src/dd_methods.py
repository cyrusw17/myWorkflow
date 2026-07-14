"""
Drawdown-control overlays for Optimized V2 residual momentum.

Long-only, lag-1 exposure. Goal: push MaxDD under the hard 35% retail gate
without destroying compound ability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.confluences import CONFLUENCES, _ann_vol, _exposure_scale, _sma, _vol_target
from src.metrics import equity_from_returns


@dataclass(frozen=True)
class DDMethod:
    id: str
    name: str
    family: str
    thesis: str
    apply: Callable[[pd.Series, pd.DataFrame], pd.Series]


def _cppi(base: pd.Series, floor_frac: float = 0.70, mult: float = 3.0) -> pd.Series:
    """
    Simple CPPI on strategy equity: exposure = clip(m * (1 - floor/E), 0, 1).
    Lagged one day via expanding simulation with lagged decision.
    """
    rets = base.fillna(0.0)
    eq = 1.0
    peak = 1.0
    out = []
    exp = 1.0
    for r in rets.values:
        out.append(float(r) * exp)
        eq *= 1.0 + float(r) * exp
        peak = max(peak, eq)
        # Floor ratchets with peak (wealth floor), cushion decides next-day exposure.
        floor = floor_frac * peak
        cushion = max(eq - floor, 0.0) / max(eq, 1e-12)
        exp = float(np.clip(mult * cushion, 0.0, 1.0))
    return pd.Series(out, index=base.index, name=base.name)


def _dd_brake(base: pd.Series, soft: float = -0.08, hard: float = -0.15, soft_exp: float = 0.45, hard_exp: float = 0.10) -> pd.Series:
    eq = equity_from_returns(base)
    dd = eq / eq.cummax() - 1.0
    exp = pd.Series(1.0, index=base.index)
    exp = exp.where(dd > soft, soft_exp)
    exp = exp.where(dd > hard, hard_exp)
    return _exposure_scale(base, exp)


def _circuit_until_recover(base: pd.Series, trip: float = -0.12, recover: float = 0.98) -> pd.Series:
    eq = equity_from_returns(base)
    peak = eq.cummax()
    dd = eq / peak - 1.0
    flat = False
    vals = []
    for i in range(len(eq)):
        if float(dd.iloc[i]) <= trip:
            flat = True
        if flat:
            if float(eq.iloc[i] / peak.iloc[i]) >= recover:
                flat = False
                vals.append(1.0)
            else:
                vals.append(0.0)
        else:
            vals.append(1.0)
    exp = pd.Series(vals, index=base.index)
    return _exposure_scale(base, exp)


def _trailing_path_stop(base: pd.Series, stop: float = -0.10, reopen_ma: int = 50) -> pd.Series:
    """
    Flatten after path drawdown trip; reopen only when equity is above its MA.
    """
    eq = equity_from_returns(base)
    peak = eq.cummax()
    dd = eq / peak - 1.0
    ma = eq.rolling(reopen_ma, min_periods=max(10, reopen_ma // 3)).mean()
    flat = False
    vals = []
    for i in range(len(eq)):
        if float(dd.iloc[i]) <= stop:
            flat = True
        if flat:
            if float(eq.iloc[i]) >= float(ma.iloc[i]) if pd.notna(ma.iloc[i]) else False:
                flat = False
                vals.append(1.0)
            else:
                vals.append(0.0)
        else:
            vals.append(1.0)
    return _exposure_scale(base, pd.Series(vals, index=base.index))


def _rolling_dd_throttle(base: pd.Series, lookback: int = 63, soft: float = -0.08, cut: float = 0.30) -> pd.Series:
    eq = equity_from_returns(base)
    roll_peak = eq.rolling(lookback, min_periods=max(10, lookback // 3)).max()
    roll_dd = eq / roll_peak - 1.0
    exp = pd.Series(1.0, index=base.index)
    exp = exp.where(roll_dd > soft, cut)
    return _exposure_scale(base, exp)


def _spy_trend_vol(base: pd.Series, prices: pd.DataFrame, target: float = 0.10) -> pd.Series:
    spy = prices["SPY"]
    gate = (spy > _sma(spy, 200)).astype(float)
    gated = _exposure_scale(base, gate)
    return _vol_target(gated, target=target, cap=1.0)


def _combo_corr_vol(base: pd.Series, prices: pd.DataFrame) -> pd.Series:
    # Anti-crowd then vol-target 10%.
    from src.confluences import apply_confluence

    a = apply_confluence("c12_corr_regime", base, prices)
    return _vol_target(a, target=0.10, cap=1.0)


def _combo_underwater_vol(base: pd.Series, prices: pd.DataFrame) -> pd.Series:
    from src.confluences import apply_confluence

    a = apply_confluence("c04_underwater_delever", base, prices)
    return _vol_target(a, target=0.10, cap=1.0)


def _combo_golden_vol(base: pd.Series, prices: pd.DataFrame) -> pd.Series:
    from src.confluences import apply_confluence

    a = apply_confluence("c17_golden_cross", base, prices)
    return _vol_target(a, target=0.12, cap=1.0)


def _time_underwater(base: pd.Series, days: int = 40, cut: float = 0.25) -> pd.Series:
    eq = equity_from_returns(base)
    peak = eq.cummax()
    below = eq < peak
    streak = below.groupby((~below).cumsum()).cumsum()
    exp = pd.Series(1.0, index=base.index)
    exp = exp.where(streak < days, cut)
    return _exposure_scale(base, exp)


def _build_dd_methods() -> list[DDMethod]:
    methods: list[DDMethod] = []

    # Reuse existing confluence catalog as DD overlays on V2.
    for c in CONFLUENCES:
        methods.append(
            DDMethod(
                id=f"conf_{c.id}",
                name=c.name,
                family="existing_confluence",
                thesis=c.thesis,
                apply=c.apply,
            )
        )

    extras = [
        DDMethod(
            "dd_vol8",
            "Vol-target 8%",
            "vol_target",
            "Cap strategy risk at ~8% ann. vol — aggressive DD control.",
            lambda b, p: _vol_target(b, target=0.08, cap=1.0),
        ),
        DDMethod(
            "dd_vol10",
            "Vol-target 10%",
            "vol_target",
            "Cap strategy risk at ~10% ann. vol.",
            lambda b, p: _vol_target(b, target=0.10, cap=1.0),
        ),
        DDMethod(
            "dd_brake_std",
            "DD brake (−8/−15)",
            "path_brake",
            "Cut to 45% after −8% path DD, 10% after −15%.",
            lambda b, p: _dd_brake(b, -0.08, -0.15, 0.45, 0.10),
        ),
        DDMethod(
            "dd_brake_tight",
            "DD brake tight (−6/−12)",
            "path_brake",
            "Faster delever: 40% at −6%, 5% at −12%.",
            lambda b, p: _dd_brake(b, -0.06, -0.12, 0.40, 0.05),
        ),
        DDMethod(
            "dd_circuit_12",
            "Circuit −12% until recover",
            "circuit",
            "Go flat after −12% path DD; reopen near peak.",
            lambda b, p: _circuit_until_recover(b, trip=-0.12, recover=0.98),
        ),
        DDMethod(
            "dd_circuit_15",
            "Circuit −15% until recover",
            "circuit",
            "Go flat after −15% path DD; reopen near peak.",
            lambda b, p: _circuit_until_recover(b, trip=-0.15, recover=0.98),
        ),
        DDMethod(
            "dd_trail_stop_10",
            "Trail stop −10% / MA reopen",
            "trail_stop",
            "Flatten after −10% path DD; reopen when equity > 50d MA.",
            lambda b, p: _trailing_path_stop(b, stop=-0.10, reopen_ma=50),
        ),
        DDMethod(
            "dd_roll_throttle",
            "63d rolling DD throttle",
            "rolling_dd",
            "If 63d equity DD ≤ −8%, run at 30% exposure.",
            lambda b, p: _rolling_dd_throttle(b, 63, -0.08, 0.30),
        ),
        DDMethod(
            "dd_time_uw",
            "Time-underwater cut",
            "time_underwater",
            "After 40 days below peak, cut to 25% until new highs.",
            lambda b, p: _time_underwater(b, days=40, cut=0.25),
        ),
        DDMethod(
            "dd_cppi_70",
            "CPPI floor 70% / m=3",
            "cppi",
            "Constant-proportion portfolio insurance vs peak wealth floor.",
            lambda b, p: _cppi(b, floor_frac=0.70, mult=3.0),
        ),
        DDMethod(
            "dd_cppi_80",
            "CPPI floor 80% / m=2.5",
            "cppi",
            "More conservative CPPI floor — prioritize capital preservation.",
            lambda b, p: _cppi(b, floor_frac=0.80, mult=2.5),
        ),
        DDMethod(
            "dd_spy_trend_vol10",
            "SPY>200 + vol 10%",
            "combo",
            "Only risk-on in SPY uptrend, then vol-target the sleeve.",
            _spy_trend_vol,
        ),
        DDMethod(
            "dd_corr_vol10",
            "Anti-crowd + vol 10%",
            "combo",
            "Cut crowded-beta regimes, then hard-cap vol at 10%.",
            _combo_corr_vol,
        ),
        DDMethod(
            "dd_uw_vol10",
            "Underwater + vol 10%",
            "combo",
            "Path underwater delever stacked with vol targeting.",
            _combo_underwater_vol,
        ),
        DDMethod(
            "dd_golden_vol12",
            "Golden-cross + vol 12%",
            "combo",
            "SPY golden-cross gate stacked with 12% vol cap.",
            _combo_golden_vol,
        ),
    ]
    methods.extend(extras)
    return methods


DD_METHODS: list[DDMethod] = _build_dd_methods()


def apply_dd_method(method_id: str, base: pd.Series, prices: pd.DataFrame) -> pd.Series:
    for m in DD_METHODS:
        if m.id == method_id:
            out = m.apply(base, prices)
            return out.reindex(base.index).fillna(0.0)
    raise KeyError(f"Unknown DD method: {method_id}")


def catalog_meta() -> list[dict]:
    return [
        {"id": m.id, "name": m.name, "family": m.family, "thesis": m.thesis}
        for m in DD_METHODS
    ]
