from __future__ import annotations

import numpy as np
import pandas as pd

from src.name_confluences import STACK_SIGNAL_IDS, signals_for_ticker

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


def _clip01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def _trade_confidence(
    ticker: str,
    score_row: pd.Series,
    sleeve_ranked: list[str],
    spy_px: pd.Series,
    dt: pd.Timestamp,
    is_tech: bool,
) -> dict:
    """
    Per-name confidence (0–100) plus component breakdown.

    Selection always uses residual rank (unchanged). V1 ignores this for sizing;
    V2 uses it to weight holdings within each sleeve.
    """
    s = score_row.dropna()
    if ticker not in s.index or s.empty:
        return {
            "confidence": 0.0,
            "components": {
                "rank_edge": 0.0,
                "score_z": 0.0,
                "dispersion": 0.0,
                "persistence": 0.0,
                "regime": 0.0,
            },
        }

    # 1) Rank edge inside its sleeve list (top picks = higher confidence)
    if ticker in sleeve_ranked and len(sleeve_ranked) > 1:
        rank_pos = sleeve_ranked.index(ticker)
        rank_edge = 1.0 - (rank_pos / max(len(sleeve_ranked) - 1, 1))
    else:
        rank_edge = 0.5

    # 2) Cross-sectional z of residual score
    mu = float(s.mean())
    sd = float(s.std()) or 1e-9
    z = (float(s.loc[ticker]) - mu) / sd
    score_z = _clip01((z + 0.5) / 2.5)  # z≈-0.5→0, z≈2→1

    # 3) Dispersion: how separated top quartile is from median (opportunity clarity)
    q75 = float(s.quantile(0.75))
    med = float(s.median())
    iqr = float(s.quantile(0.75) - s.quantile(0.25)) or 1e-9
    dispersion = _clip01((q75 - med) / iqr)

    # 4) Persistence proxy: ticker vs sleeve median (positive residual surplus)
    persistence = _clip01(0.5 + (float(s.loc[ticker]) - med) / (2.0 * iqr))

    # 5) Soft regime backdrop (does not gate trades)
    if dt in spy_px.index:
        loc = spy_px.index.get_loc(dt)
        if isinstance(loc, slice):
            loc = loc.start
        i = int(loc)
        window = spy_px.iloc[max(0, i - 199) : i + 1]
        above_200 = float(spy_px.iloc[i] >= window.mean()) if len(window) >= 20 else 0.5
        rets = spy_px.pct_change().iloc[max(0, i - 20) : i + 1]
        vol = float(rets.std() * np.sqrt(252)) if len(rets) > 5 else 0.15
        calm = _clip01(1.0 - max(vol - 0.12, 0.0) / 0.30)
        regime = 0.6 * above_200 + 0.4 * calm
    else:
        regime = 0.5

    # Tech sleeve slightly higher baseline context (informational only)
    tech_boost = 0.03 if is_tech else 0.0

    conf = 100.0 * _clip01(
        0.30 * rank_edge
        + 0.25 * score_z
        + 0.15 * dispersion
        + 0.15 * persistence
        + 0.15 * regime
        + tech_boost
    )
    return {
        "confidence": round(conf, 1),
        "components": {
            "rank_edge": round(100.0 * rank_edge, 1),
            "score_z": round(100.0 * score_z, 1),
            "dispersion": round(100.0 * dispersion, 1),
            "persistence": round(100.0 * persistence, 1),
            "regime": round(100.0 * regime, 1),
        },
    }


# Locked after Stage-A/B + local refine sweeps (src/optimize_v2.py).
# Key finding: retail survival is driven by confidence → cash buffer + mild
# shrink-to-equal, NOT aggressive name overweighting.
DEFAULT_V2_SIZE: dict = {
    "power": 0.25,
    "shrink": 0.90,
    "floor": 12.0,
    "max_name_frac": 0.35,
    "gross_mode": "conf_mean",
    "gross_floor": 0.35,
    "gross_ceil": 1.0,
    "conf_lo": 52.0,
    "conf_hi": 78.0,
}


def _confidence_sleeve_weights(
    names: list[str],
    sleeve_gross: float,
    conf_map: dict[str, dict],
    cols: list[str],
    size_cfg: dict,
) -> pd.Series:
    """Map confidence → sleeve weights with shrink, power tilt, and name caps."""
    w = pd.Series(0.0, index=cols)
    if not names or sleeve_gross <= 0:
        return w

    n = len(names)
    equal = np.full(n, 1.0 / n, dtype=float)
    floor = float(size_cfg.get("floor", 5.0))
    power = float(size_cfg.get("power", 1.0))
    shrink = float(np.clip(size_cfg.get("shrink", 0.0), 0.0, 1.0))
    max_frac = float(np.clip(size_cfg.get("max_name_frac", 1.0), 1.0 / n, 1.0))

    raw = np.array(
        [max(float(conf_map[t]["confidence"]), floor) ** power for t in names],
        dtype=float,
    )
    if raw.sum() <= 0:
        tilt = equal.copy()
    else:
        tilt = raw / raw.sum()

    # Blend toward equal weight (James–Stein style), then enforce concentration cap.
    mix = (1.0 - shrink) * tilt + shrink * equal
    mix = mix / mix.sum()

    # Cap oversized names; redistribute residual to names under the cap.
    for _ in range(8):
        over = mix > max_frac + 1e-12
        if not over.any():
            break
        excess = float((mix[over] - max_frac).sum())
        mix[over] = max_frac
        under = ~over
        if not under.any() or mix[under].sum() <= 0:
            break
        mix[under] = mix[under] + excess * (mix[under] / mix[under].sum())

    mix = mix / mix.sum()
    for t, wt in zip(names, mix):
        w.loc[t] = sleeve_gross * float(wt)
    return w


def _gross_from_confidence(conf_vals: list[float], size_cfg: dict) -> float:
    """Scale book exposure down when average confidence is weak (cash buffer)."""
    mode = str(size_cfg.get("gross_mode", "full"))
    lo_g = float(size_cfg.get("gross_floor", 1.0))
    hi_g = float(size_cfg.get("gross_ceil", 1.0))
    if mode == "full" or not conf_vals:
        return 1.0
    mean_c = float(np.mean(conf_vals))
    if mode == "conf_mean":
        conf_lo = float(size_cfg.get("conf_lo", 40.0))
        conf_hi = float(size_cfg.get("conf_hi", 75.0))
        span = max(conf_hi - conf_lo, 1e-9)
        t = _clip01((mean_c - conf_lo) / span)
        return float(lo_g + t * (hi_g - lo_g))
    return 1.0


def prepare_residual_momentum(
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
) -> dict:
    """
    Precompute residual scores + per-rebalance picks/confidence.

    Selection is identical for V1/V2; only sizing differs downstream.
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
    spy_px = prices[spy_col]

    betas = pd.DataFrame(index=rets.index, columns=cols, dtype=float)
    for c in cols:
        cov = rets[c].rolling(lookback_beta).cov(spy)
        var = spy.rolling(lookback_beta).var()
        betas[c] = cov / var.replace(0, np.nan)

    resid = rets[cols] - betas.mul(spy, axis=0)
    score = resid.shift(skip).rolling(formation).sum()
    warmup = lookback_beta + formation + skip + 1

    events: list[dict] = []
    last_reb = -10**9
    for i, dt in enumerate(prices.index):
        if i < warmup:
            continue
        if (i - last_reb) < rebalance_every:
            continue

        s = score.loc[dt].dropna()
        tech_ranked = [t for t in _ranked(s) if t in tech_cols]
        other_ranked = [t for t in _ranked(s) if t in other_cols]
        pick_tech = tech_ranked[: min(n_tech, len(tech_ranked))]
        pick_other = other_ranked[: min(n_other, len(other_ranked))] if other_weight > 1e-12 else []

        conf_map: dict[str, dict] = {}
        for t in list(pick_tech) + list(pick_other):
            sleeve = tech_ranked if t in tech else other_ranked
            conf_map[t] = _trade_confidence(
                ticker=t,
                score_row=s,
                sleeve_ranked=sleeve,
                spy_px=spy_px,
                dt=dt,
                is_tech=t in tech,
            )
        events.append(
            {
                "i": i,
                "dt": dt,
                "pick_tech": pick_tech,
                "pick_other": pick_other,
                "conf_map": conf_map,
            }
        )
        last_reb = i

    return {
        "prices_index": prices.index,
        "cols": cols,
        "tech_cols": tech_cols,
        "rets": rets,
        "tech_weight": tech_weight,
        "other_weight": other_weight,
        "rebalance_every": rebalance_every,
        "cost_bps": cost_bps,
        "warmup": warmup,
        "events": events,
        "n_tech": n_tech,
        "n_other": n_other,
    }


def allocate_residual_momentum(
    prepared: dict,
    size_by_confidence: bool = False,
    size_cfg: dict | None = None,
    boost_panels: dict[str, pd.DataFrame] | None = None,
    boost_mode: str | None = None,
    boost_mult: float = 1.5,
    boost_signal_id: str | None = None,
    boost_min_count: int = 2,
) -> tuple[pd.Series, dict]:
    """
    Turn prepared picks into a return series under V1 or V2 sizing.

    Optional trade-level confluence boost:
      - boost_mode="any": if any name confluence is True → weight × boost_mult
      - boost_mode="stack": if ≥ boost_min_count signals True → × boost_mult
      - boost_mode="single": only boost_signal_id gates the × boost_mult
    After boosts, sleeve weights are renormalized to keep sleeve gross fixed.
    """
    cols: list[str] = prepared["cols"]
    rets: pd.DataFrame = prepared["rets"]
    tech_weight = float(prepared["tech_weight"])
    other_weight = float(prepared["other_weight"])
    cost = float(prepared["cost_bps"]) / 10000.0
    warmup = int(prepared["warmup"])
    v2_cfg = {**DEFAULT_V2_SIZE, **(size_cfg or {})}
    boost_on = boost_panels is not None and boost_mode in {"any", "single", "stack"}
    boost_mult = float(max(boost_mult, 1.0))
    min_count = int(max(boost_min_count, 1))

    port = pd.Series(0.0, index=prepared["prices_index"], name="residual_momentum")
    weights = pd.Series(0.0, index=cols)
    trade_log: list[dict] = []
    gross_hist: list[float] = []
    boost_hits = 0
    boost_checks = 0
    event_by_i = {e["i"]: e for e in prepared["events"]}

    def _apply_boost(names: list[str], base_w: pd.Series, sleeve_gross: float, dt) -> tuple[pd.Series, dict[str, bool]]:
        nonlocal boost_hits, boost_checks
        w = pd.Series(0.0, index=cols)
        flags: dict[str, bool] = {}
        if not names or sleeve_gross <= 0:
            return w, flags
        raw = []
        for t in names:
            bw = float(base_w.get(t, 0.0))
            boosted = False
            n_hits = 0
            if boost_on and bw > 0:
                boost_checks += 1
                sigs = signals_for_ticker(boost_panels, t, dt)  # type: ignore[arg-type]
                if boost_mode == "stack":
                    n_hits = int(sum(1 for sid in STACK_SIGNAL_IDS if sigs.get(sid)))
                else:
                    n_hits = int(sum(1 for v in sigs.values() if v))
                if boost_mode == "any":
                    boosted = n_hits >= 1
                elif boost_mode == "stack":
                    boosted = n_hits >= min_count
                elif boost_mode == "single" and boost_signal_id:
                    boosted = bool(sigs.get(boost_signal_id, False))
                if boosted:
                    boost_hits += 1
            flags[t] = boosted
            raw.append(bw * (boost_mult if boosted else 1.0))
        arr = np.array(raw, dtype=float)
        if arr.sum() <= 0:
            return w, flags
        arr = arr / arr.sum() * sleeve_gross
        for t, wt in zip(names, arr):
            w.loc[t] = float(wt)
        return w, flags

    for i, dt in enumerate(prepared["prices_index"]):
        if i < warmup:
            continue

        if i in event_by_i:
            ev = event_by_i[i]
            pick_tech = ev["pick_tech"]
            pick_other = ev["pick_other"]
            conf_map = ev["conf_map"]

            def _base_sleeve(names: list[str], sleeve_gross: float) -> pd.Series:
                w = pd.Series(0.0, index=cols)
                if not names or sleeve_gross <= 0:
                    return w
                if not size_by_confidence:
                    w.loc[names] = sleeve_gross / len(names)
                    return w
                return _confidence_sleeve_weights(names, sleeve_gross, conf_map, cols, v2_cfg)

            new_w = pd.Series(0.0, index=cols)
            boost_flags: dict[str, bool] = {}
            if pick_tech and tech_weight > 1e-12:
                sleeve_gross = tech_weight if pick_other else 1.0
                base = _base_sleeve(pick_tech, sleeve_gross)
                if boost_on:
                    part, flags = _apply_boost(pick_tech, base, sleeve_gross, dt)
                    boost_flags.update(flags)
                    new_w = new_w + part
                else:
                    new_w = new_w + base
            if pick_other and other_weight > 1e-12:
                sleeve_gross = other_weight if pick_tech else 1.0
                base = _base_sleeve(pick_other, sleeve_gross)
                if boost_on:
                    part, flags = _apply_boost(pick_other, base, sleeve_gross, dt)
                    boost_flags.update(flags)
                    new_w = new_w + part
                else:
                    new_w = new_w + base
            if new_w.sum() <= 0:
                port.loc[dt] = 0.0
                continue

            # Preserve relative sleeve mix; then optional V2 cash buffer on top.
            new_w = new_w / new_w.sum()
            conf_vals = [float(conf_map[t]["confidence"]) for t in new_w[new_w > 0].index]
            if size_by_confidence:
                gross = _gross_from_confidence(conf_vals, v2_cfg)
                new_w = new_w * gross
                gross_hist.append(gross)
            else:
                gross = 1.0

            for t in new_w[new_w > 0].index:
                if float(weights.get(t, 0.0)) <= 0:
                    conf = conf_map[t]
                    trade_log.append(
                        {
                            "date": dt.strftime("%Y-%m-%d"),
                            "ticker": t,
                            "is_tech": t in set(prepared["tech_cols"]),
                            "weight": round(float(new_w.loc[t]), 6),
                            "confidence": conf["confidence"],
                            "confidence_components": conf["components"],
                            "sizing": "confidence" if size_by_confidence else "equal",
                            "gross": round(float(gross), 4),
                            "confluence_boost": bool(boost_flags.get(t, False)),
                            "boost_mult": boost_mult if boost_flags.get(t, False) else 1.0,
                        }
                    )

            turnover = (new_w - weights).abs().sum() / 2.0
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * new_w).sum()) - turnover * cost
            weights = new_w
        else:
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())

    port = port.fillna(0.0)
    live = port.iloc[warmup:]
    years = max((live.index[-1] - live.index[0]).days / 365.25, 1e-9) if len(live) > 1 else 1e-9
    months = years * 12.0
    n_trades = len(trade_log)
    n_tech_trades = sum(1 for t in trade_log if t["is_tech"])
    conf_vals = [float(t["confidence"]) for t in trade_log]
    if boost_on:
        version = f"boost_{boost_mode}" + (f"_{boost_signal_id}" if boost_signal_id else "")
        if size_by_confidence:
            version = "v2_" + version
        else:
            version = "v1_" + version
    else:
        version = "v2_confidence_sized" if size_by_confidence else "v1_equal_weight"
    stats = {
        "mode": "tech_weight_residual_momentum",
        "version": version,
        "size_by_confidence": bool(size_by_confidence),
        "size_cfg": dict(v2_cfg) if size_by_confidence else None,
        "boost": {
            "enabled": bool(boost_on),
            "mode": boost_mode,
            "signal_id": boost_signal_id,
            "mult": boost_mult,
            "min_count": min_count if boost_mode == "stack" else None,
            "hit_rate": (boost_hits / boost_checks) if boost_checks else None,
            "hits": boost_hits,
            "checks": boost_checks,
        },
        "tech_weight": tech_weight,
        "n_tech": prepared["n_tech"],
        "n_other": prepared["n_other"],
        "rebalance_every": prepared["rebalance_every"],
        "n_trades": n_trades,
        "trades_per_month": (n_trades / months) if months > 0 else 0.0,
        "tech_trade_share": (n_tech_trades / n_trades) if n_trades else 0.0,
        "tech_universe": sorted(prepared["tech_cols"]),
        "trade_log": trade_log,
        "avg_gross": round(float(np.mean(gross_hist)), 4) if gross_hist else 1.0,
        "confidence": {
            "note": (
                "V2 uses confidence to size holdings within sleeves + optional cash buffer."
                if size_by_confidence
                else "Background only on V1 — does not affect selection or equal sizing."
            ),
            "method": (
                "0–100 blend of sleeve rank edge, residual z-score, cross-sectional "
                "dispersion, persistence vs median, and soft SPY regime backdrop"
            ),
            "mean": round(float(np.mean(conf_vals)), 2) if conf_vals else None,
            "median": round(float(np.median(conf_vals)), 2) if conf_vals else None,
            "p25": round(float(np.percentile(conf_vals, 25)), 2) if conf_vals else None,
            "p75": round(float(np.percentile(conf_vals, 75)), 2) if conf_vals else None,
            "min": round(float(np.min(conf_vals)), 2) if conf_vals else None,
            "max": round(float(np.max(conf_vals)), 2) if conf_vals else None,
            "buckets": {
                "low_<40": int(sum(1 for c in conf_vals if c < 40)),
                "mid_40_70": int(sum(1 for c in conf_vals if 40 <= c < 70)),
                "high_>=70": int(sum(1 for c in conf_vals if c >= 70)),
            },
        },
    }
    return port, stats


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
    size_by_confidence: bool = False,
    size_cfg: dict | None = None,
) -> tuple[pd.Series, dict]:
    """
    Long-only residual momentum with a fixed technology portfolio weight.

    V1 (size_by_confidence=False): equal-weight within sleeves; confidence is
    background metadata only.
    V2 (size_by_confidence=True): same name selection; holdings sized from
    confidence via size_cfg (tilt power, shrink-to-equal, name caps, optional
    confidence-scaled gross / cash buffer).
    """
    prepared = prepare_residual_momentum(
        prices,
        spy_col=spy_col,
        lookback_beta=lookback_beta,
        formation=formation,
        skip=skip,
        n_tech=n_tech,
        n_other=n_other,
        tech_weight=tech_weight,
        rebalance_every=rebalance_every,
        cost_bps=cost_bps,
        tech_tickers=tech_tickers,
    )
    return allocate_residual_momentum(
        prepared,
        size_by_confidence=size_by_confidence,
        size_cfg=size_cfg,
    )

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
