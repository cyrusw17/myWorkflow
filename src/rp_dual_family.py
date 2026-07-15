"""
RP + Dual-mom family — expandable catalog of sleeve / filter / trade-count variants.

Add a new strategy by appending one dict to FAMILY_SPECS (then re-run the lab).
Groups on the page: baseline · sleeve · filter · trade_ladder
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.ftmo_strategies import (
    COMMOD,
    CRYPTO,
    FX,
    INDICES,
    STOCK_CFD,
    _align_cols,
    _inverse_vol_weights,
    _portfolio_from_weights,
    _safe_rets,
    _vol_scale_series,
    apply_daily_brake,
)

# Expand stock sleeve so mcap / vol filters have room to work.
STOCK_EXTENDED = STOCK_CFD + [
    "TSLA",
    "NFLX",
    "COST",
    "CRM",
    "ORCL",
    "INTC",
    "BA",
    "DIS",
    "WMT",
    "KO",
]

# Approx market caps ($B) — research proxies for filtering, not live quotes.
# Update when you add tickers; missing → treated as small.
MCAP_B: dict[str, float] = {
    # mega / large stocks
    "AAPL": 3200, "MSFT": 3100, "NVDA": 3000, "GOOGL": 2100, "AMZN": 2000,
    "META": 1400, "AVGO": 900, "TSLA": 800, "ORCL": 450, "CRM": 280,
    "COST": 400, "NFLX": 400, "WMT": 550, "JPM": 650, "XOM": 500,
    "KO": 280, "DIS": 200, "BA": 140, "AMD": 220, "INTC": 110,
    # index / ETF proxies (AUM-ish / notional scale for filter ranking)
    "SPY": 500, "QQQ": 250, "DIA": 35, "IWM": 60,
    "GLD": 60, "SLV": 12, "USO": 4,
    # crypto network "size" proxy
    "BTC-USD": 1200, "ETH-USD": 350,
    # FX majors get large notionals; crosses slightly lower
    "EURUSD=X": 900, "GBPUSD=X": 500, "USDJPY=X": 700, "AUDUSD=X": 250,
    "USDCAD=X": 200, "USDCHF=X": 180, "NZDUSD=X": 90,
    "EURJPY=X": 150, "GBPJPY=X": 120,
}

SLEEVES: dict[str, list[str]] = {
    "all": list(dict.fromkeys(FX + INDICES + COMMOD + CRYPTO + STOCK_EXTENDED)),
    "stocks": STOCK_EXTENDED,
    "crypto": CRYPTO,
    "fx": FX,
    "indices": INDICES,
    "commod": COMMOD,
}

FAMILY_TICKERS = SLEEVES["all"]


@dataclass(frozen=True)
class FamilySpec:
    id: str
    name: str
    group: str  # baseline | sleeve | filter | trade_ladder
    sleeve: str
    thesis: str
    n_holdings: int | None = None  # dual-mom top-N; None = default 3
    min_mcap_b: float | None = None
    min_ann_vol: float | None = None  # absolute vol floor
    vol_percentile: float | None = None  # keep names above this cross-section pct
    target_vol: float = 0.09
    rp_weight: float = 0.62
    dual_weight: float = 0.25
    grind_weight: float = 0.13


def _filter_universe(
    prices: pd.DataFrame,
    tickers: list[str],
    *,
    min_mcap_b: float | None = None,
    min_ann_vol: float | None = None,
    vol_percentile: float | None = None,
) -> list[str]:
    cols = _align_cols(prices, tickers)
    if not cols:
        return []
    keep = cols
    if min_mcap_b is not None:
        keep = [c for c in keep if MCAP_B.get(c, 0.0) >= min_mcap_b]
    if not keep:
        return []
    rets = _safe_rets(prices[keep])
    vol = rets.rolling(63, min_periods=21).std() * np.sqrt(252.0)
    # Use latest non-null vol row for static membership (lagged decision still on weights)
    last = vol.ffill().iloc[-1]
    if min_ann_vol is not None:
        keep = [c for c in keep if float(last.get(c, 0.0) or 0.0) >= min_ann_vol]
    if vol_percentile is not None and keep:
        sub = last.reindex(keep).dropna()
        if len(sub):
            thr = float(sub.quantile(vol_percentile))
            keep = [c for c in keep if float(last.get(c, 0.0) or 0.0) >= thr]
    return keep


def _dual_mom_on(
    prices: pd.DataFrame,
    cols: list[str],
    *,
    lookback: int = 126,
    n_top: int = 3,
    target_vol: float = 0.10,
) -> pd.Series:
    cols = _align_cols(prices, cols)
    if len(cols) < 1:
        return pd.Series(0.0, index=prices.index, name="dual")
    n_top = max(1, min(n_top, len(cols)))
    px = prices[cols]
    rets = _safe_rets(px)
    abs_mom = px / px.shift(lookback) - 1.0
    ranks = abs_mom.rank(axis=1, ascending=False)
    long = ((ranks <= n_top) & (abs_mom > 0)).astype(float)
    w = long.div(long.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=3.0)
    return _vol_scale_series(raw, target_vol, cap=1.8).rename("dual")


def _risk_parity_on(
    prices: pd.DataFrame,
    cols: list[str],
    *,
    target_vol: float = 0.10,
) -> pd.Series:
    cols = _align_cols(prices, cols)
    if len(cols) < 1:
        return pd.Series(0.0, index=prices.index, name="rp")
    px = prices[cols]
    rets = _safe_rets(px)
    w = _inverse_vol_weights(rets, 42)
    raw = _portfolio_from_weights(rets, w, cost_bps=1.5)
    return _vol_scale_series(raw, target_vol, lookback=42, cap=1.5).rename("rp")


def _index_grind_on(
    prices: pd.DataFrame,
    cols: list[str],
    *,
    target_vol: float = 0.085,
) -> pd.Series:
    """Long-only TSMOM breadth grind on whatever sleeve we have (fallback = equal)."""
    cols = _align_cols(prices, cols)
    if not cols:
        return pd.Series(0.0, index=prices.index, name="grind")
    # Prefer index tickers when present; else use sleeve itself
    prefer = _align_cols(prices, [c for c in cols if c in INDICES]) or cols
    px = prices[prefer]
    rets = _safe_rets(px)
    mom = px / px.shift(63) - 1.0
    sig = np.sign(mom).clip(lower=0.0)
    w = sig.div(sig.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    breadth = (sig > 0).sum(axis=1)
    w = w.mul((breadth >= max(1, len(prefer) // 2)).astype(float), axis=0)
    raw = _portfolio_from_weights(rets, w, cost_bps=1.0)
    return _vol_scale_series(raw, target_vol, lookback=42, cap=1.2).rename("grind")


def build_rp_dual_family(
    prices: pd.DataFrame,
    spec: FamilySpec,
) -> tuple[pd.Series, dict]:
    """Run one catalog entry; returns returns + diagnostics for the page."""
    base_cols = SLEEVES.get(spec.sleeve, SLEEVES["all"])
    cols = _filter_universe(
        prices,
        base_cols,
        min_mcap_b=spec.min_mcap_b,
        min_ann_vol=spec.min_ann_vol,
        vol_percentile=spec.vol_percentile,
    )
    n_top = spec.n_holdings if spec.n_holdings is not None else 3
    if len(cols) < 1:
        empty = pd.Series(0.0, index=prices.index, name=spec.id)
        return empty, {"n_assets": 0, "assets": [], "n_holdings": n_top}

    a = _risk_parity_on(prices, cols, target_vol=0.10)
    b = _dual_mom_on(prices, cols, n_top=n_top, target_vol=0.10)
    c = _index_grind_on(prices, cols, target_vol=0.085)
    mix = (
        spec.rp_weight * a.fillna(0)
        + spec.dual_weight * b.fillna(0)
        + spec.grind_weight * c.fillna(0)
    )
    mix = mix.clip(-0.018, 0.018)
    out = _vol_scale_series(mix, spec.target_vol, lookback=32, cap=1.45)
    out = apply_daily_brake(out, 0.009, 0.016).rename(spec.id)
    diag = {
        "n_assets": len(cols),
        "assets": cols,
        "n_holdings": n_top,
        "sleeve": spec.sleeve,
        "min_mcap_b": spec.min_mcap_b,
        "min_ann_vol": spec.min_ann_vol,
        "vol_percentile": spec.vol_percentile,
    }
    return out, diag


# ---------------------------------------------------------------------------
# Catalog — APPEND HERE to grow the lab. Page groups by `group`.
# ---------------------------------------------------------------------------
FAMILY_SPECS: list[FamilySpec] = [
    # Baseline
    FamilySpec(
        "rp_dual_base",
        "RP + Dual (baseline)",
        "baseline",
        "all",
        "Original FTMO winner template — multi-asset RP + dual-mom + grind",
        n_holdings=3,
    ),
    # Sleeve isolations
    FamilySpec(
        "rp_dual_stocks",
        "Stocks only",
        "sleeve",
        "stocks",
        "Same engine, stock-CFD sleeve only",
        n_holdings=4,
    ),
    FamilySpec(
        "rp_dual_crypto",
        "Crypto only",
        "sleeve",
        "crypto",
        "Same engine on BTC/ETH only — high-vol stress test",
        n_holdings=2,
        target_vol=0.08,
    ),
    FamilySpec(
        "rp_dual_fx",
        "FX only",
        "sleeve",
        "fx",
        "Majors + crosses only",
        n_holdings=3,
    ),
    FamilySpec(
        "rp_dual_indices",
        "Indices only",
        "sleeve",
        "indices",
        "US500 / NAS100 / US30 / Russell proxies only",
        n_holdings=2,
    ),
    FamilySpec(
        "rp_dual_commod",
        "Commodities only",
        "sleeve",
        "commod",
        "Gold / silver / oil proxies only",
        n_holdings=2,
    ),
    # Filters (per expanded universe / each sleeve family)
    FamilySpec(
        "rp_dual_himcap",
        "High market-cap filter",
        "filter",
        "all",
        "Only names with approx mcap/AUM ≥ $200B",
        n_holdings=3,
        min_mcap_b=200.0,
    ),
    FamilySpec(
        "rp_dual_stocks_himcap",
        "Stocks · high mcap",
        "filter",
        "stocks",
        "Stock CFDs with approx mcap ≥ $400B",
        n_holdings=4,
        min_mcap_b=400.0,
    ),
    FamilySpec(
        "rp_dual_hivol",
        "High volatility filter",
        "filter",
        "all",
        "Keep names in the top half of 63d realized vol",
        n_holdings=3,
        vol_percentile=0.50,
    ),
    FamilySpec(
        "rp_dual_stocks_hivol",
        "Stocks · high vol",
        "filter",
        "stocks",
        "Stock CFDs above cross-section 63d vol median",
        n_holdings=4,
        vol_percentile=0.50,
    ),
    FamilySpec(
        "rp_dual_crypto_hivol",
        "Crypto · high vol",
        "filter",
        "crypto",
        "Crypto sleeve requiring ≥40% ann. realized vol",
        n_holdings=2,
        min_ann_vol=0.40,
        target_vol=0.08,
    ),
    FamilySpec(
        "rp_dual_fx_himcap",
        "FX · major notionals",
        "filter",
        "fx",
        "FX pairs with large notional proxy (≥ $200B scale)",
        n_holdings=3,
        min_mcap_b=200.0,
    ),
    # Trade-count ladders (increasing N holdings / activity)
    FamilySpec(
        "rp_dual_n2",
        "Baseline · 2 holdings",
        "trade_ladder",
        "all",
        "Dual-mom top-2 — fewer concurrent names",
        n_holdings=2,
    ),
    FamilySpec(
        "rp_dual_n4",
        "Baseline · 4 holdings",
        "trade_ladder",
        "all",
        "Dual-mom top-4 — more concurrent names",
        n_holdings=4,
    ),
    FamilySpec(
        "rp_dual_n6",
        "Baseline · 6 holdings",
        "trade_ladder",
        "all",
        "Dual-mom top-6 — highest activity ladder rung",
        n_holdings=6,
    ),
    FamilySpec(
        "rp_dual_stocks_n2",
        "Stocks · 2 holdings",
        "trade_ladder",
        "stocks",
        "Stock sleeve, dual-mom top-2",
        n_holdings=2,
    ),
    FamilySpec(
        "rp_dual_stocks_n4",
        "Stocks · 4 holdings",
        "trade_ladder",
        "stocks",
        "Stock sleeve, dual-mom top-4",
        n_holdings=4,
    ),
    FamilySpec(
        "rp_dual_stocks_n6",
        "Stocks · 6 holdings",
        "trade_ladder",
        "stocks",
        "Stock sleeve, dual-mom top-6",
        n_holdings=6,
    ),
]


GROUP_ORDER = ["baseline", "sleeve", "filter", "trade_ladder"]
GROUP_LABELS = {
    "baseline": "Baseline — RP + Dual-mom",
    "sleeve": "By asset sleeve",
    "filter": "Market-cap & volatility filters",
    "trade_ladder": "Trade-count ladders (increasing holdings)",
}


def catalog_summary() -> list[dict]:
    return [
        {
            "id": s.id,
            "name": s.name,
            "group": s.group,
            "sleeve": s.sleeve,
            "thesis": s.thesis,
            "n_holdings": s.n_holdings,
            "min_mcap_b": s.min_mcap_b,
            "min_ann_vol": s.min_ann_vol,
            "vol_percentile": s.vol_percentile,
            "target_vol": s.target_vol,
        }
        for s in FAMILY_SPECS
    ]
