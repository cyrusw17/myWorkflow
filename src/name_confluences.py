"""
Per-name confluence signals for trade-level sizing boosts.

Each signal is a boolean DataFrame aligned to prices (True = confluence present).
Signals are lagged 1 day so rebalance decisions never peek.

Designed to be *selective* (~25–55% hit rate on residual-mom picks) so that a
1.5× weight boost actually redistributes capital inside the sleeve.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class NameConfluence:
    id: str
    name: str
    thesis: str


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=max(5, n // 3)).mean()


def _rsi(prices: pd.Series, n: int = 14) -> pd.Series:
    delta = prices.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    au = up.rolling(n, min_periods=n).mean()
    ad = down.rolling(n, min_periods=n).mean()
    rs = au / ad.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


NAME_CONFLUENCES: list[NameConfluence] = [
    NameConfluence(
        "n01_golden",
        "Name golden cross",
        "50dma > 200dma and price above 50dma — structured uptrend.",
    ),
    NameConfluence(
        "n02_rs_trend",
        "RS + 50dma",
        "Beating SPY over 21d while price holds above its 50dma.",
    ),
    NameConfluence(
        "n03_rsi_sweet",
        "RSI sweet spot",
        "14d RSI between 45 and 65 — momentum without euphoria.",
    ),
    NameConfluence(
        "n04_breakout20",
        "20d breakout",
        "Close at/above the prior 20-day high (continuation).",
    ),
    NameConfluence(
        "n05_accel",
        "Momentum accel",
        "21d return stronger than one-third of 63d return (acceleration).",
    ),
    NameConfluence(
        "n06_reclaim200",
        "Fresh 200dma reclaim",
        "Above 200dma now, but traded below it sometime in the prior 63d.",
    ),
    NameConfluence(
        "n07_vol_contract",
        "Vol contraction",
        "21d realized vol below 63d vol — quieter backdrop for trend.",
    ),
]

# Curated stack for the core "extra confluence" boost book (selective).
STACK_SIGNAL_IDS: tuple[str, ...] = (
    "n03_rsi_sweet",
    "n04_breakout20",
    "n05_accel",
    "n06_reclaim200",
)


def build_name_signal_panels(prices: pd.DataFrame, spy_col: str = "SPY") -> dict[str, pd.DataFrame]:
    """
    Return {signal_id: DataFrame[bool]} for every non-SPY column.
    Already lag-1 for use at rebalance date dt.
    """
    names = [c for c in prices.columns if c != spy_col]
    px = prices[names]
    spy = prices[spy_col]

    s50 = px.apply(lambda s: _sma(s, 50))
    s200 = px.apply(lambda s: _sma(s, 200))
    rsi = px.apply(lambda s: _rsi(s, 14))

    ret21 = px / px.shift(21) - 1.0
    ret63 = px / px.shift(63) - 1.0
    spy21 = spy / spy.shift(21) - 1.0

    # Prior 20d high measured without today's close in the window → use shift.
    high20 = px.shift(1).rolling(20, min_periods=10).max()
    below200_recent = (px < s200).rolling(63, min_periods=20).max().fillna(0.0) > 0

    logret = np.log(px / px.shift(1))
    vol21 = logret.rolling(21, min_periods=10).std() * np.sqrt(252)
    vol63 = logret.rolling(63, min_periods=20).std() * np.sqrt(252)

    raw = {
        "n01_golden": (s50 > s200) & (px > s50),
        "n02_rs_trend": ret21.gt(spy21, axis=0) & (px > s50),
        "n03_rsi_sweet": (rsi >= 45.0) & (rsi <= 65.0),
        "n04_breakout20": px >= high20,
        "n05_accel": ret21 > (ret63 / 3.0),
        "n06_reclaim200": (px > s200) & below200_recent,
        "n07_vol_contract": vol21 < vol63,
    }
    return {k: v.shift(1).fillna(False).astype(bool) for k, v in raw.items()}


def signals_for_ticker(
    panels: dict[str, pd.DataFrame],
    ticker: str,
    dt: pd.Timestamp,
) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for sid, panel in panels.items():
        if ticker not in panel.columns or dt not in panel.index:
            out[sid] = False
            continue
        out[sid] = bool(panel.at[dt, ticker])
    return out


def catalog_meta() -> list[dict]:
    return [{"id": c.id, "name": c.name, "thesis": c.thesis} for c in NAME_CONFLUENCES]
