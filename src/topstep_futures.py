"""
CME futures books for the Topstep lab.

Topstep / TopstepX is futures-only (no stocks, FX spot, or CFDs).
Universe = continuous Yahoo futures (=F). Strategies are daily proxies —
not live TopstepX fills, fees, or tick-level margins.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.ftmo_strategies import (
    _align_cols,
    _inverse_vol_weights,
    _portfolio_from_weights,
    _safe_rets,
    _tsmom_signal,
    _vol_scale_series,
)

# --- CME continuous futures (Yahoo) ---
INDEX_FUTS = ["ES=F", "NQ=F", "YM=F", "RTY=F"]
COMMOD_FUTS = ["CL=F", "GC=F", "SI=F", "NG=F"]
RATES_FUTS = ["ZB=F", "ZN=F", "ZF=F"]
FX_FUTS = ["6E=F", "6J=F", "6B=F"]
CRYPTO_FUTS = ["BTC=F"]

TOPSTEP_FUTURES = INDEX_FUTS + COMMOD_FUTS + RATES_FUTS + FX_FUTS + CRYPTO_FUTS


@dataclass(frozen=True)
class FuturesStratMeta:
    id: str
    name: str
    family: str
    thesis: str
    markets: str


def _vol_target_book(
    prices: pd.DataFrame,
    cols: list[str],
    *,
    target_vol: float,
    signal: pd.DataFrame | None = None,
    cost_bps: float = 1.5,
) -> pd.Series:
    use = _align_cols(prices, cols)
    if not use:
        return pd.Series(0.0, index=prices.index, name="empty")
    px = prices[use]
    rets = _safe_rets(px)
    if signal is None:
        w = _inverse_vol_weights(rets)
    else:
        sig = signal.reindex(columns=use).fillna(0.0)
        base = _inverse_vol_weights(rets)
        w = base * sig
        s = w.abs().sum(axis=1).replace(0, np.nan)
        w = w.div(s, axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=cost_bps)
    return _vol_scale_series(raw, target_vol)


def strat_index_futures_rp(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    return _vol_target_book(prices, INDEX_FUTS, target_vol=target_vol).rename("index_futs_rp")


def strat_index_futures_tsmom(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    use = _align_cols(prices, INDEX_FUTS)
    sig = _tsmom_signal(prices[use]) if use else None
    return _vol_target_book(prices, INDEX_FUTS, target_vol=target_vol, signal=sig).rename(
        "index_futs_tsmom"
    )


def strat_es_only(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    cols = _align_cols(prices, ["ES=F", "MES=F"]) or _align_cols(prices, ["ES=F"])
    if not cols:
        return pd.Series(0.0, index=prices.index, name="es_only")
    rets = _safe_rets(prices[cols[0]].to_frame())
    raw = rets.iloc[:, 0]
    # long-only when 20d momentum > 0, else flat (futures Combine usually directional)
    mom = prices[cols[0]] / prices[cols[0]].shift(20) - 1.0
    gate = (mom.shift(1) > 0).astype(float)
    return _vol_scale_series(raw * gate, target_vol).rename("es_only")


def strat_nq_es_relative(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    need = _align_cols(prices, ["ES=F", "NQ=F"])
    if len(need) < 2:
        return pd.Series(0.0, index=prices.index, name="nq_es_rel")
    rets = _safe_rets(prices[need])
    # long stronger 63d relative momentum, short weaker (market-neutral-ish)
    mom = prices[need] / prices[need].shift(63) - 1.0
    rank = mom.rank(axis=1, pct=True)
    w = (rank - 0.5) * 2.0  # [-1,1]
    raw = _portfolio_from_weights(rets, w)
    return _vol_scale_series(raw, target_vol).rename("nq_es_rel")


def strat_commodity_trend(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    use = _align_cols(prices, COMMOD_FUTS)
    sig = _tsmom_signal(prices[use]) if use else None
    return _vol_target_book(prices, COMMOD_FUTS, target_vol=target_vol, signal=sig).rename(
        "commod_trend"
    )


def strat_rates_fx_defensive(prices: pd.DataFrame, target_vol: float = 0.07) -> pd.Series:
    return _vol_target_book(
        prices, RATES_FUTS + FX_FUTS, target_vol=target_vol
    ).rename("rates_fx_def")


def strat_cross_asset_tsmom(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    use = _align_cols(prices, TOPSTEP_FUTURES)
    sig = _tsmom_signal(prices[use], lookbacks=(21, 63, 126)) if use else None
    return _vol_target_book(prices, TOPSTEP_FUTURES, target_vol=target_vol, signal=sig).rename(
        "xa_tsmom"
    )


def strat_futures_risk_parity(prices: pd.DataFrame, target_vol: float = 0.10) -> pd.Series:
    return _vol_target_book(prices, TOPSTEP_FUTURES, target_vol=target_vol).rename("futs_rp")


def strat_equity_index_grind(prices: pd.DataFrame, target_vol: float = 0.08) -> pd.Series:
    """Slow index-futures carry: inverse-vol long bias with soft TSMOM gate."""
    use = _align_cols(prices, INDEX_FUTS)
    if not use:
        return pd.Series(0.0, index=prices.index, name="index_grind")
    rets = _safe_rets(prices[use])
    w = _inverse_vol_weights(rets)
    mom = _tsmom_signal(prices[use], lookbacks=(63, 126))
    # keep only non-negative sleeve (long or flat)
    w = w * mom.clip(lower=0.0)
    s = w.sum(axis=1).replace(0, np.nan)
    w = w.div(s, axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w)
    return _vol_scale_series(raw, target_vol).rename("index_grind")


def strat_gold_rates(prices: pd.DataFrame, target_vol: float = 0.08) -> pd.Series:
    return _vol_target_book(prices, ["GC=F", "SI=F"] + RATES_FUTS, target_vol=target_vol).rename(
        "gold_rates"
    )


FUTURES_BUILDERS: dict[str, callable] = {
    "futs_rp_vt10": lambda p: strat_futures_risk_parity(p, 0.10),
    "futs_rp_vt7": lambda p: strat_futures_risk_parity(p, 0.07),
    "index_futs_rp_vt10": lambda p: strat_index_futures_rp(p, 0.10),
    "index_futs_tsmom_vt10": lambda p: strat_index_futures_tsmom(p, 0.10),
    "index_grind_futs_vt8": lambda p: strat_equity_index_grind(p, 0.08),
    "es_only_vt10": lambda p: strat_es_only(p, 0.10),
    "nq_es_rel_vt10": lambda p: strat_nq_es_relative(p, 0.10),
    "commod_trend_vt10": lambda p: strat_commodity_trend(p, 0.10),
    "rates_fx_def_vt7": lambda p: strat_rates_fx_defensive(p, 0.07),
    "xa_tsmom_vt10": lambda p: strat_cross_asset_tsmom(p, 0.10),
    "gold_rates_vt8": lambda p: strat_gold_rates(p, 0.08),
}

FUTURES_META: dict[str, FuturesStratMeta] = {
    "futs_rp_vt10": FuturesStratMeta(
        "futs_rp_vt10",
        "CME risk parity @ 10% vol",
        "futures_rp",
        "Inverse-vol across index / commodity / rates / FX / BTC futures — diversified CME book",
        "ES NQ YM RTY · CL GC SI NG · ZB ZN ZF · 6E 6J 6B · BTC",
    ),
    "futs_rp_vt7": FuturesStratMeta(
        "futs_rp_vt7",
        "CME risk parity @ 7% vol",
        "futures_rp",
        "Lower-vol inverse-vol futures basket — defensive Combine pace",
        "Full CME basket",
    ),
    "index_futs_rp_vt10": FuturesStratMeta(
        "index_futs_rp_vt10",
        "Index futures RP @ 10%",
        "index_futs",
        "ES / NQ / YM / RTY inverse-vol only — equity-index futures sleeve",
        "ES NQ YM RTY",
    ),
    "index_futs_tsmom_vt10": FuturesStratMeta(
        "index_futs_tsmom_vt10",
        "Index futures TSMOM @ 10%",
        "index_futs",
        "Multi-horizon time-series momentum on equity-index futures",
        "ES NQ YM RTY",
    ),
    "index_grind_futs_vt8": FuturesStratMeta(
        "index_grind_futs_vt8",
        "Index futures grind @ 8%",
        "index_futs",
        "Long-biased index futures with TSMOM gate — slow Combine grind",
        "ES NQ YM RTY",
    ),
    "es_only_vt10": FuturesStratMeta(
        "es_only_vt10",
        "ES-only trend @ 10%",
        "single_name",
        "Vol-targeted ES with 20d momentum gate — classic TopstepX index future",
        "ES",
    ),
    "nq_es_rel_vt10": FuturesStratMeta(
        "nq_es_rel_vt10",
        "NQ vs ES relative @ 10%",
        "relative",
        "Long/short stronger 63d relative momentum between NQ and ES",
        "NQ ES",
    ),
    "commod_trend_vt10": FuturesStratMeta(
        "commod_trend_vt10",
        "Commodity futures trend @ 10%",
        "commodity",
        "TSMOM on CL / GC / SI / NG",
        "CL GC SI NG",
    ),
    "rates_fx_def_vt7": FuturesStratMeta(
        "rates_fx_def_vt7",
        "Rates + FX futures defensive @ 7%",
        "defensive",
        "Inverse-vol Treasury + FX futures sleeve",
        "ZB ZN ZF · 6E 6J 6B",
    ),
    "xa_tsmom_vt10": FuturesStratMeta(
        "xa_tsmom_vt10",
        "Cross-asset futures TSMOM @ 10%",
        "cross_asset",
        "Multi-horizon momentum across the full CME Topstep basket",
        "Full CME basket",
    ),
    "gold_rates_vt8": FuturesStratMeta(
        "gold_rates_vt8",
        "Gold + rates futures @ 8%",
        "defensive",
        "GC/SI with Treasury futures — metals/rates diversifier",
        "GC SI · ZB ZN ZF",
    ),
}

# Screen order — no Phase-1 speedups; one winner used board-wide
FUTURES_CANDIDATES = list(FUTURES_BUILDERS.keys())
