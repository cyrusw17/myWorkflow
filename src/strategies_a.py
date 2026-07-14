from __future__ import annotations

import numpy as np
import pandas as pd

# Technology sleeve for the ≥30% tech trade floor.
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


def _ranked_by_score(score_row: pd.Series) -> list[str]:
    return score_row.sort_values(ascending=False).index.tolist()


def _ensure_tech_holdings(
    names: list[str],
    ranked: list[str],
    tech: set[str],
    min_share: float,
) -> list[str]:
    """Swap weakest non-tech for best unused tech until holding floor is met."""
    if not names or min_share <= 0:
        return names
    needed = max(1, int(np.ceil(len(names) * min_share)))
    rank_pos = {t: i for i, t in enumerate(ranked)}
    names = list(names)
    for cand in ranked:
        tech_held = [x for x in names if x in tech]
        if len(tech_held) >= needed:
            break
        if cand not in tech or cand in names:
            continue
        non_tech = [x for x in names if x not in tech]
        if not non_tech:
            break
        worst = max(non_tech, key=lambda x: rank_pos.get(x, 10**9))
        names = [cand if x == worst else x for x in names]
    return names


def residual_momentum_returns(
    prices: pd.DataFrame,
    spy_col: str = "SPY",
    lookback_beta: int = 90,
    formation: int = 63,
    skip: int = 1,
    n_hold: int = 8,
    rebalance_every: int = 1,
    entries_per_rebalance: int = 1,
    min_tech_share: float = 0.30,
    cost_bps: float = 5.0,
    tech_tickers: set[str] | None = None,
) -> tuple[pd.Series, dict]:
    """
    Long-only residual momentum with operational targets:
    - ≥ min_tech_share of entries (trades) in technology names
    - ~20 trades/month via forced daily rotation (1 entry / trading day)

    A trade is an entry: weight going from 0 → >0.
    """
    tech = set(tech_tickers or TECH_TICKERS)
    cols = [c for c in prices.columns if c != spy_col]
    available_tech = sorted(c for c in cols if c in tech)
    if not available_tech:
        raise ValueError("Universe has no technology tickers; cannot enforce tech trade floor")

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

    for i, dt in enumerate(prices.index):
        if i < warmup:
            continue

        if i % rebalance_every != 0:
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            continue

        s = score.loc[dt].dropna()
        if len(s) < max(3, n_hold // 2):
            port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * weights).sum())
            continue

        ranked = _ranked_by_score(s)
        rank_pos = {t: i for i, t in enumerate(ranked)}
        held = [t for t in weights.index if float(weights[t]) > 0]

        hist_n = len(trade_log)
        hist_tech = sum(1 for t in trade_log if t["is_tech"])
        tech_share = (hist_tech / hist_n) if hist_n else 0.0
        need_tech_entries = tech_share < min_tech_share

        if not held:
            # Seed full sleeve once (counts toward trades; rate settles after).
            new_names = ranked[:n_hold]
            new_names = _ensure_tech_holdings(new_names, ranked, tech, min_tech_share)
        else:
            # Force-rotate into names not currently held so every day books a real entry.
            # entries_per_rebalance=1 on daily rebalance ≈ ~21 trades/month.
            n_rotate = min(entries_per_rebalance, n_hold, len(held))
            held_worst_first = sorted(held, key=lambda t: rank_pos.get(t, 10**9), reverse=True)
            drop = set(held_worst_first[:n_rotate])
            kept = [t for t in held if t not in drop]

            # Never re-add a currently held name (including ones we just dropped).
            candidates = [t for t in ranked if t not in held]
            if need_tech_entries:
                tech_cands = [t for t in candidates if t in tech]
                other_cands = [t for t in candidates if t not in tech]
                candidates = tech_cands + other_cands

            if len(candidates) < n_rotate:
                # Exhausted unique names — allow drop set members as last resort.
                candidates = candidates + [t for t in ranked if t in drop and t not in candidates]

            adds = candidates[:n_rotate]
            # If tech floor on holdings would break, prefer a tech add.
            trial = kept + adds
            tech_needed = max(1, int(np.ceil(n_hold * min_tech_share)))
            if sum(1 for t in trial if t in tech) < tech_needed:
                tech_add = next((t for t in ranked if t in tech and t not in held), None)
                if tech_add is not None:
                    adds = [tech_add] + [a for a in adds if a != tech_add]
                    adds = adds[:n_rotate]

            new_names = (kept + adds)[:n_hold]
            for t in ranked:
                if len(new_names) >= n_hold:
                    break
                if t not in new_names and t not in held:
                    new_names.append(t)
            # Fill any remaining slots from rank list if universe is short.
            for t in ranked:
                if len(new_names) >= n_hold:
                    break
                if t not in new_names:
                    new_names.append(t)
            new_names = _ensure_tech_holdings(new_names, ranked, tech, min_tech_share)

        new_w = pd.Series(0.0, index=cols)
        if new_names:
            new_w.loc[new_names] = 1.0 / len(new_names)

        for t in new_names:
            if float(weights.get(t, 0.0)) <= 0:
                trade_log.append(
                    {"date": dt.strftime("%Y-%m-%d"), "ticker": t, "is_tech": t in tech}
                )

        turnover = (new_w - weights).abs().sum() / 2.0
        port.loc[dt] = float((rets.loc[dt, cols].fillna(0.0) * new_w).sum()) - turnover * cost
        weights = new_w

    port = port.fillna(0.0)
    live = port.iloc[warmup:]
    if len(live) > 1:
        years = max((live.index[-1] - live.index[0]).days / 365.25, 1e-9)
    else:
        years = 1e-9
    months = years * 12.0
    n_trades = len(trade_log)
    n_tech = sum(1 for t in trade_log if t["is_tech"])
    stats = {
        "n_trades": n_trades,
        "n_tech_trades": n_tech,
        "tech_trade_share": (n_tech / n_trades) if n_trades else 0.0,
        "trades_per_month": (n_trades / months) if months > 0 else 0.0,
        "n_hold": n_hold,
        "rebalance_every": rebalance_every,
        "entries_per_rebalance": entries_per_rebalance,
        "min_tech_share": min_tech_share,
        "tech_universe": available_tech,
    }
    return port, stats
