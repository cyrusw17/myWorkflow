"""
FTMO-oriented multi-asset quant strategies (daily Yahoo CFD proxies).

Research base (classic quant literature, adapted for FTMO static 10% / daily 5%):
  - Moskowitz / Ooi / Pedersen time-series momentum (TSMOM)
  - Cross-sectional equity momentum (Jegadeesh-Titman style)
  - Dual momentum (Gary Antonacci)
  - Risk parity / inverse-vol (risk budgeting)
  - Volatility targeting (Barroso / Santa-Clara; Moreira-Muir)
  - Donchian / ATR breakout trend
  - Short-horizon FX mean reversion (careful — often fails DD gates)
  - Crypto trend dampened by vol targeting
  - Defensive blend: low-vol multi-asset grind tuned for challenge survival

Long-only on equities/stock-CFDs; FX / metal / crypto sleeves may be signed
(FTMO CFDs allow shorts; our Robinhood equity mandate does not apply here).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# --- Universes (Yahoo proxies for FTMO CFD classes) ---
FX = [
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "AUDUSD=X",
    "USDCAD=X",
    "USDCHF=X",
    "NZDUSD=X",
    "EURJPY=X",
    "GBPJPY=X",
]
INDICES = ["SPY", "QQQ", "DIA", "IWM"]  # US500 / NAS100 / US30 / Russell proxies
COMMOD = ["GLD", "SLV", "USO"]
CRYPTO = ["BTC-USD", "ETH-USD"]
STOCK_CFD = [
    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "GOOGL",
    "AMZN",
    "AMD",
    "AVGO",
    "JPM",
    "XOM",
]

FTMO_TICKERS = FX + INDICES + COMMOD + CRYPTO + STOCK_CFD


@dataclass(frozen=True)
class StratMeta:
    id: str
    name: str
    family: str
    thesis: str
    markets: str


def _align_cols(prices: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if c in prices.columns]


def _safe_rets(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _rolling_vol(rets: pd.DataFrame | pd.Series, lookback: int = 21) -> pd.DataFrame | pd.Series:
    return rets.rolling(lookback, min_periods=max(5, lookback // 3)).std() * np.sqrt(252.0)


def _vol_scale_series(asset_rets: pd.Series, target_vol: float, lookback: int = 21, cap: float = 2.5) -> pd.Series:
    vol = _rolling_vol(asset_rets, lookback)
    lever = (target_vol / vol.replace(0, np.nan)).clip(upper=cap).shift(1).fillna(0.0)
    return asset_rets * lever


def _portfolio_from_weights(
    rets: pd.DataFrame,
    weights: pd.DataFrame,
    cost_bps: float = 2.0,
) -> pd.Series:
    """Weights known at t apply to returns at t (caller must lag if needed)."""
    w = weights.reindex_like(rets).fillna(0.0)
    # Lag weights one day — decisions use info through t-1
    w = w.shift(1).fillna(0.0)
    gross = w.abs().sum(axis=1).clip(lower=1e-12)
    # Soft renorm if somehow over-levered beyond 1.5
    scale = (1.5 / gross).clip(upper=1.0)
    w = w.mul(scale, axis=0)
    port = (w * rets).sum(axis=1)
    turnover = w.diff().abs().sum(axis=1).fillna(0.0)
    costs = turnover * (cost_bps / 10000.0)
    return (port - costs).rename("strategy")


def _tsmom_signal(prices: pd.DataFrame, lookbacks: tuple[int, ...] = (21, 63, 126)) -> pd.DataFrame:
    """Sign of multi-horizon excess return; average for smoother signal."""
    sig = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for lb in lookbacks:
        mom = prices / prices.shift(lb) - 1.0
        sig = sig + np.sign(mom.fillna(0.0))
    return (sig / float(len(lookbacks))).clip(-1.0, 1.0)


def _inverse_vol_weights(rets: pd.DataFrame, lookback: int = 21) -> pd.DataFrame:
    vol = _rolling_vol(rets, lookback).replace(0, np.nan)
    inv = 1.0 / vol
    inv = inv.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    s = inv.sum(axis=1).replace(0, np.nan)
    return inv.div(s, axis=0).fillna(0.0)


def strat_tsmom_fx(prices: pd.DataFrame, target_vol: float = 0.08) -> pd.Series:
    cols = _align_cols(prices, FX)
    px = prices[cols]
    rets = _safe_rets(px)
    sig = _tsmom_signal(px)
    # Equal risk across pairs then portfolio vol target
    base_w = sig / max(len(cols), 1)
    raw = _portfolio_from_weights(rets, base_w)
    return _vol_scale_series(raw, target_vol).rename("tsmom_fx")


def strat_tsmom_multi(prices: pd.DataFrame, target_vol: float = 0.09) -> pd.Series:
    cols = _align_cols(prices, FX + INDICES + COMMOD + CRYPTO)
    px = prices[cols]
    rets = _safe_rets(px)
    sig = _tsmom_signal(px, (21, 63, 126))
    # Inverse-vol risk budget on absolute signal
    inv = _inverse_vol_weights(rets)
    w = (sig * inv)
    # Normalize to unit gross risk budget
    gross = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.div(gross, axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w)
    return _vol_scale_series(raw, target_vol, cap=2.0).rename("tsmom_multi")


def strat_xs_mom_stocks(prices: pd.DataFrame, formation: int = 63, n: int = 4, target_vol: float = 0.10) -> pd.Series:
    cols = _align_cols(prices, STOCK_CFD)
    px = prices[cols]
    rets = _safe_rets(px)
    mom = px / px.shift(formation) - 1.0
    # Long-only top-n equal weight
    ranks = mom.rank(axis=1, ascending=False)
    w = (ranks <= n).astype(float)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=4.0)
    return _vol_scale_series(raw, target_vol, cap=1.5).rename("xs_mom_stocks")


def strat_dual_mom(prices: pd.DataFrame, lookback: int = 126, target_vol: float = 0.08) -> pd.Series:
    """Relative strength among risk assets; cash if absolute momentum negative."""
    cols = _align_cols(prices, INDICES + COMMOD + ["BTC-USD"] + STOCK_CFD[:6])
    px = prices[cols]
    rets = _safe_rets(px)
    abs_mom = px / px.shift(lookback) - 1.0
    # Pick top 3 with positive abs mom
    ranks = abs_mom.rank(axis=1, ascending=False)
    long = ((ranks <= 3) & (abs_mom > 0)).astype(float)
    w = long.div(long.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=3.0)
    return _vol_scale_series(raw, target_vol, cap=1.8).rename("dual_mom")


def strat_risk_parity(prices: pd.DataFrame, target_vol: float = 0.07) -> pd.Series:
    cols = _align_cols(prices, FX[:6] + INDICES + COMMOD)
    px = prices[cols]
    rets = _safe_rets(px)
    # Always long risk parity (defensive)
    w = _inverse_vol_weights(rets, 42)
    raw = _portfolio_from_weights(rets, w, cost_bps=1.5)
    return _vol_scale_series(raw, target_vol, lookback=42, cap=1.5).rename("risk_parity")


def strat_donchian_trend(prices: pd.DataFrame, channel: int = 55, target_vol: float = 0.08) -> pd.Series:
    cols = _align_cols(prices, FX + INDICES + COMMOD)
    px = prices[cols]
    rets = _safe_rets(px)
    hi = px.rolling(channel).max()
    lo = px.rolling(channel).min()
    # +1 above prior high, -1 below prior low, else 0 (Turtle Lite)
    prev_hi = hi.shift(1)
    prev_lo = lo.shift(1)
    sig = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    sig = sig.mask(px > prev_hi, 1.0)
    sig = sig.mask(px < prev_lo, -1.0)
    # Carry last signal (position persistence)
    sig = sig.replace(0.0, np.nan).ffill().fillna(0.0)
    inv = _inverse_vol_weights(rets)
    w = (sig * inv)
    gross = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.div(gross, axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=3.0)
    return _vol_scale_series(raw, target_vol, cap=1.8).rename("donchian")


def strat_fx_meanrev(prices: pd.DataFrame, lookback: int = 5, z_entry: float = 1.25, target_vol: float = 0.06) -> pd.Series:
    cols = _align_cols(prices, FX)
    px = prices[cols]
    rets = _safe_rets(px)
    mu = px.rolling(lookback).mean()
    sd = px.rolling(lookback).std().replace(0, np.nan)
    z = (px - mu) / sd
    # Fade extremes; long-only-ish bias soft for dollar assets → signed FX is OK
    sig = -np.sign(z.fillna(0.0))
    sig = sig.where(z.abs() >= z_entry, 0.0)
    w = sig / max(len(cols), 1)
    raw = _portfolio_from_weights(rets, w, cost_bps=2.5)
    return _vol_scale_series(raw, target_vol, lookback=15, cap=1.5).rename("fx_meanrev")


def strat_crypto_trend(prices: pd.DataFrame, target_vol: float = 0.08) -> pd.Series:
    cols = _align_cols(prices, CRYPTO)
    if not cols:
        return pd.Series(0.0, index=prices.index, name="crypto_trend")
    px = prices[cols]
    rets = _safe_rets(px)
    sig = _tsmom_signal(px, (10, 21, 63))
    # Heavily damp — crypto vol destroys FTMO accounts
    inv = _inverse_vol_weights(rets, 14)
    w = (sig.clip(lower=0.0) * inv)  # long-only crypto sleeve
    gross = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.div(gross, axis=0).fillna(0.0) * 0.5  # max 50% book in crypto sleeve pre vol-target
    raw = _portfolio_from_weights(rets, w, cost_bps=5.0)
    return _vol_scale_series(raw, target_vol, lookback=14, cap=1.2).rename("crypto_trend")


def strat_index_grind(prices: pd.DataFrame, target_vol: float = 0.06) -> pd.Series:
    """Ultra-conservative equity-index long: slow TSMOM + tight vol target."""
    cols = _align_cols(prices, INDICES)
    px = prices[cols]
    rets = _safe_rets(px)
    sig = _tsmom_signal(px, (63, 126)).clip(lower=0.0)  # long-only
    w = sig.div(sig.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    # Move to cash when breadth weak
    breadth = (sig > 0).sum(axis=1)
    w = w.mul((breadth >= 2).astype(float), axis=0)
    raw = _portfolio_from_weights(rets, w, cost_bps=1.0)
    return _vol_scale_series(raw, target_vol, lookback=42, cap=1.2).rename("index_grind")


def strat_atr_trail(prices: pd.DataFrame, atr_lb: int = 20, mult: float = 2.5, target_vol: float = 0.08) -> pd.Series:
    """Wilder-style ATR channel trend on FX+indices (using close range proxy)."""
    cols = _align_cols(prices, FX[:6] + INDICES)
    px = prices[cols]
    rets = _safe_rets(px)
    # True range proxy from close-to-close
    tr = px.diff().abs()
    atr = tr.rolling(atr_lb).mean()
    upper = px.rolling(atr_lb).max()
    lower = px - mult * atr
    # Long when close near upper channel; flat/short near weakness
    pos = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    pos = pos.mask(px >= upper.shift(1), 1.0)
    pos = pos.mask(px < lower.shift(1), -0.5)
    pos = pos.replace(0.0, np.nan).ffill().fillna(0.0)
    inv = _inverse_vol_weights(rets)
    w = pos * inv
    gross = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.div(gross, axis=0).fillna(0.0)
    raw = _portfolio_from_weights(rets, w, cost_bps=2.5)
    return _vol_scale_series(raw, target_vol, cap=1.6).rename("atr_trail")


def strat_boll_safe(prices: pd.DataFrame, lb: int = 20, target_vol: float = 0.05) -> pd.Series:
    """Bollinger mean-reversion only when realized vol is subdued."""
    cols = _align_cols(prices, INDICES + FX[:4])
    px = prices[cols]
    rets = _safe_rets(px)
    ma = px.rolling(lb).mean()
    sd = px.rolling(lb).std()
    z = (px - ma) / sd.replace(0, np.nan)
    rv = _rolling_vol(rets, 21)
    low_vol = rv.lt(rv.rolling(126).median())
    sig = (-np.sign(z.fillna(0.0))).where(z.abs() > 1.5, 0.0)
    sig = sig.where(low_vol.fillna(False), 0.0)
    w = sig / max(len(cols), 1)
    raw = _portfolio_from_weights(rets, w, cost_bps=2.0)
    return _vol_scale_series(raw, target_vol, lookback=21, cap=1.2).rename("boll_safe")


def strat_ftmo_grind(prices: pd.DataFrame, target_vol: float = 0.055) -> pd.Series:
    """
    Challenge-survival blend: 50% multi TSMOM + 30% risk parity + 20% index grind,
    then hard vol-target so a −5% day is statistically rare.
    """
    a = strat_tsmom_multi(prices, target_vol=0.10)
    b = strat_risk_parity(prices, target_vol=0.08)
    c = strat_index_grind(prices, target_vol=0.07)
    mix = (0.50 * a.fillna(0) + 0.30 * b.fillna(0) + 0.20 * c.fillna(0))
    # Daily loss soft-brake: clip single-day raw move before final vol scale
    mix = mix.clip(-0.025, 0.025)
    return _vol_scale_series(mix, target_vol, lookback=42, cap=1.5).rename("ftmo_grind")


def strat_challenge_sprinter(prices: pd.DataFrame, target_vol: float = 0.12) -> pd.Series:
    """
    Challenge-paced book: dual-mom + multi TSMOM with higher vol target to hit
    +10% before boredom, but daily brake to protect the 5% daily loss rule.
    """
    a = strat_dual_mom(prices, target_vol=0.14)
    b = strat_tsmom_multi(prices, target_vol=0.12)
    c = strat_xs_mom_stocks(prices, target_vol=0.12)
    mix = 0.45 * a.fillna(0) + 0.35 * b.fillna(0) + 0.20 * c.fillna(0)
    mix = mix.clip(-0.03, 0.03)
    return _vol_scale_series(mix, target_vol, lookback=21, cap=2.0).rename("challenge_sprint")


def strat_pass_then_defend(prices: pd.DataFrame) -> pd.Series:
    """
    Two-regime synthetic: higher risk when far from +10%, defend after cushion.
    Uses only lagged equity of a base book — no peeking on future returns.
    """
    base = strat_dual_mom(prices, target_vol=0.14)
    eq = (1.0 + base.fillna(0.0)).cumprod()
    # Lag regime so today's scale uses yesterday's equity only
    eq_lag = eq.shift(1).fillna(1.0)
    # Below +4%: sprint; +4–10%: normal; above path peak defend
    scale = pd.Series(1.0, index=base.index)
    scale = scale.where(eq_lag >= 1.04, 1.25)
    scale = scale.where(eq_lag < 1.10, 0.70)
    scale = scale.where(eq_lag < 1.08, 0.85)
    out = (base.fillna(0.0) * scale.clip(0.4, 1.35)).clip(-0.028, 0.028)
    return apply_daily_brake(out, 0.012, 0.022).rename("pass_defend")


def strat_gold_fx_defensive(prices: pd.DataFrame, target_vol: float = 0.06) -> pd.Series:
    """Defensive: long GLD when rising + FX TSMOM sleeve at low vol."""
    g = _align_cols(prices, ["GLD"])
    fx = strat_tsmom_fx(prices, target_vol=0.07)
    if not g:
        return fx.rename("gold_fx")
    grets = _safe_rets(prices[g])["GLD"]
    gsig = np.sign(prices["GLD"] / prices["GLD"].shift(63) - 1.0).clip(lower=0.0).fillna(0.0)
    gold = _vol_scale_series(grets * gsig.shift(1).fillna(0.0), 0.05, cap=1.2)
    mix = 0.45 * gold.fillna(0) + 0.55 * fx.fillna(0)
    return _vol_scale_series(mix, target_vol, lookback=42, cap=1.3).rename("gold_fx")


def apply_daily_brake(rets: pd.Series, soft: float = 0.012, hard: float = 0.025) -> pd.Series:
    """
    Path-aware intra-challenge brake using closed days only:
    after a soft down day, cut next-day exposure; after hard, go flat next day.
    """
    r = rets.fillna(0.0)
    out = []
    scale = 1.0
    for val in r:
        out.append(float(val) * scale)
        if val <= -hard:
            scale = 0.0
        elif val <= -soft:
            scale = 0.35
        else:
            # heal toward 1
            scale = min(1.0, scale + 0.15) if scale < 1.0 else 1.0
            if val > 0:
                scale = min(1.0, scale + 0.1)
    return pd.Series(out, index=r.index, name=getattr(rets, "name", "braked"))


def strat_rp_dual_blend(prices: pd.DataFrame, target_vol: float = 0.09) -> pd.Series:
    """Primary FTMO candidate: dominate with risk-parity, add dual-mom thrust."""
    a = strat_risk_parity(prices, target_vol=0.10)
    b = strat_dual_mom(prices, target_vol=0.10)
    c = strat_index_grind(prices, target_vol=0.085)
    mix = 0.62 * a.fillna(0) + 0.25 * b.fillna(0) + 0.13 * c.fillna(0)
    mix = mix.clip(-0.018, 0.018)
    out = _vol_scale_series(mix, target_vol, lookback=32, cap=1.45)
    return apply_daily_brake(out, 0.009, 0.016).rename("rp_dual")


STRATEGY_BUILDERS: dict[str, callable] = {
    "rp_dual_blend": lambda p: strat_rp_dual_blend(p, 0.09),
    "ftmo_grind": lambda p: apply_daily_brake(strat_ftmo_grind(p, 0.07), 0.010, 0.020),
    "ftmo_grind_raw": lambda p: strat_ftmo_grind(p, 0.07),
    "challenge_sprint": lambda p: apply_daily_brake(strat_challenge_sprinter(p, 0.12), 0.011, 0.020),
    "pass_defend": lambda p: strat_pass_then_defend(p),
    "tsmom_multi_vt8": lambda p: apply_daily_brake(strat_tsmom_multi(p, 0.08), 0.012, 0.022),
    "tsmom_multi_vt12": lambda p: apply_daily_brake(strat_tsmom_multi(p, 0.12), 0.012, 0.022),
    "tsmom_fx_vt8": lambda p: apply_daily_brake(strat_tsmom_fx(p, 0.08), 0.012, 0.022),
    "tsmom_fx_vt12": lambda p: apply_daily_brake(strat_tsmom_fx(p, 0.12), 0.012, 0.022),
    "risk_parity_vt7": lambda p: strat_risk_parity(p, 0.07),
    "risk_parity_vt10": lambda p: strat_risk_parity(p, 0.10),
    "dual_mom_vt8": lambda p: apply_daily_brake(strat_dual_mom(p, target_vol=0.08), 0.012, 0.022),
    "dual_mom_vt12": lambda p: apply_daily_brake(strat_dual_mom(p, target_vol=0.12), 0.011, 0.020),
    "index_grind_vt6": lambda p: strat_index_grind(p, 0.06),
    "index_grind_vt10": lambda p: strat_index_grind(p, 0.10),
    "donchian_vt8": lambda p: apply_daily_brake(strat_donchian_trend(p, target_vol=0.08), 0.012, 0.025),
    "xs_mom_stocks_vt9": lambda p: apply_daily_brake(strat_xs_mom_stocks(p, target_vol=0.09), 0.012, 0.022),
    "xs_mom_stocks_vt12": lambda p: apply_daily_brake(strat_xs_mom_stocks(p, target_vol=0.12), 0.011, 0.020),
    "gold_fx_vt6": lambda p: strat_gold_fx_defensive(p, 0.06),
    "gold_fx_vt10": lambda p: apply_daily_brake(strat_gold_fx_defensive(p, 0.10), 0.012, 0.022),
    "crypto_trend_vt7": lambda p: apply_daily_brake(strat_crypto_trend(p, 0.07), 0.010, 0.018),
    "atr_trail_vt8": lambda p: apply_daily_brake(strat_atr_trail(p, target_vol=0.08), 0.012, 0.022),
    "fx_meanrev_vt6": lambda p: strat_fx_meanrev(p, target_vol=0.06),
    "boll_safe_vt5": lambda p: strat_boll_safe(p, target_vol=0.05),
}


STRATEGY_META: dict[str, StratMeta] = {
    "rp_dual_blend": StratMeta(
        "rp_dual_blend",
        "RP + Dual-mom blend",
        "survival",
        "55%→62% risk-parity + dual-mom + index grind @ ~9% vol with daily brake — fail-first design",
        "FX + indices + commod + stocks",
    ),
    "ftmo_grind": StratMeta(
        "ftmo_grind",
        "FTMO Grind (blend + brake)",
        "survival",
        "50/30/20 multi-TSMOM + risk-parity + index grind, ~7% vol target, daily brake — built to pass",
        "FX + indices + commod",
    ),
    "ftmo_grind_raw": StratMeta(
        "ftmo_grind_raw",
        "FTMO Grind (no brake)",
        "survival",
        "Same blend without daily brake — measures brake value",
        "FX + indices + commod",
    ),
    "challenge_sprint": StratMeta(
        "challenge_sprint",
        "Challenge sprinter 12% vol",
        "survival",
        "Dual-mom + multi-TSMOM + stock XS mom at challenge pace with hard daily brake",
        "Multi-asset",
    ),
    "pass_defend": StratMeta(
        "pass_defend",
        "Pass-then-defend",
        "survival",
        "Sprint while below +10%, de-lever after cushion — regime on lagged equity only",
        "Multi-asset",
    ),
    "tsmom_multi_vt8": StratMeta(
        "tsmom_multi_vt8",
        "Multi-asset TSMOM 8% vol",
        "trend",
        "Moskowitz-style signed TSMOM across FX/indices/commod/crypto, vol-targeted + brake",
        "FX + indices + commod + crypto",
    ),
    "tsmom_multi_vt12": StratMeta(
        "tsmom_multi_vt12",
        "Multi-asset TSMOM 12% vol",
        "trend",
        "Higher-pace multi TSMOM for faster Phase-1 hits",
        "FX + indices + commod + crypto",
    ),
    "tsmom_fx_vt8": StratMeta(
        "tsmom_fx_vt8",
        "FX-only TSMOM 8% vol",
        "trend",
        "Major/cross FX time-series momentum — core FTMO forex book",
        "FX",
    ),
    "tsmom_fx_vt12": StratMeta(
        "tsmom_fx_vt12",
        "FX-only TSMOM 12% vol",
        "trend",
        "Faster FX TSMOM — more Phase-1 throughput, watch daily loss",
        "FX",
    ),
    "risk_parity_vt7": StratMeta(
        "risk_parity_vt7",
        "Risk parity 7% vol",
        "defensive",
        "Inverse-vol long risk budget — slow, consistent, lower fail rate",
        "FX + indices + commod",
    ),
    "risk_parity_vt10": StratMeta(
        "risk_parity_vt10",
        "Risk parity 10% vol",
        "defensive",
        "Same RP engine sized to reach targets sooner",
        "FX + indices + commod",
    ),
    "dual_mom_vt8": StratMeta(
        "dual_mom_vt8",
        "Dual momentum 8% vol",
        "trend",
        "Antonacci dual mom: relative strength + absolute filter → cash when trend dies",
        "Indices + commod + stocks + BTC",
    ),
    "dual_mom_vt12": StratMeta(
        "dual_mom_vt12",
        "Dual momentum 12% vol",
        "trend",
        "Challenge-paced dual momentum with brake",
        "Indices + commod + stocks + BTC",
    ),
    "index_grind_vt6": StratMeta(
        "index_grind_vt6",
        "Index grind 6% vol",
        "defensive",
        "Long-only index TSMOM with breadth filter — US500/NAS100/US30/Russell proxies",
        "Indices",
    ),
    "index_grind_vt10": StratMeta(
        "index_grind_vt10",
        "Index grind 10% vol",
        "defensive",
        "Faster index grind for Phase-1 pace",
        "Indices",
    ),
    "donchian_vt8": StratMeta(
        "donchian_vt8",
        "Donchian 55 breakout",
        "breakout",
        "Turtle-lite channel breakout on FX+indices+commod",
        "FX + indices + commod",
    ),
    "xs_mom_stocks_vt9": StratMeta(
        "xs_mom_stocks_vt9",
        "Stock-CFD cross-sectional mom",
        "momentum",
        "Top-4 of 10 liquid stock CFDs by 63d momentum — closest to our equity residual-mom DNA",
        "Stock CFDs",
    ),
    "xs_mom_stocks_vt12": StratMeta(
        "xs_mom_stocks_vt12",
        "Stock-CFD XS mom 12% vol",
        "momentum",
        "Faster stock-CFD momentum sleeve",
        "Stock CFDs",
    ),
    "gold_fx_vt6": StratMeta(
        "gold_fx_vt6",
        "Gold + FX defensive",
        "defensive",
        "Trend-filtered GLD sleeve + FX TSMOM — crisis-aware mix",
        "FX + gold",
    ),
    "gold_fx_vt10": StratMeta(
        "gold_fx_vt10",
        "Gold + FX 10% vol",
        "defensive",
        "Same gold/FX mix at challenge pace",
        "FX + gold",
    ),
    "crypto_trend_vt7": StratMeta(
        "crypto_trend_vt7",
        "Crypto trend dampened",
        "crypto",
        "BTC/ETH long-only TSMOM heavily vol-damped — stress test for FTMO crypto CFDs",
        "Crypto",
    ),
    "atr_trail_vt8": StratMeta(
        "atr_trail_vt8",
        "ATR trailing trend",
        "trend",
        "ATR channel continuation on FX+indices",
        "FX + indices",
    ),
    "fx_meanrev_vt6": StratMeta(
        "fx_meanrev_vt6",
        "FX short-horizon mean-rev",
        "meanrev",
        "5d z-score fade on FX — often fails quiet trends; included as contrast",
        "FX",
    ),
    "boll_safe_vt5": StratMeta(
        "boll_safe_vt5",
        "Bollinger safe mean-rev",
        "meanrev",
        "Bollinger fade only in below-median realized-vol regimes",
        "Indices + FX",
    ),
}
