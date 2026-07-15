"""
RP + Dual-mom family lab — baseline + sleeve / filter / trade-count variants.

Append specs in src/rp_dual_family.py::FAMILY_SPECS to grow the page.
Outputs site/data/rp_dual_lab.json for site/rp-dual-lab.html.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.data import load_universe
from src.ftmo_rules import FtmoRules, rolling_challenges, summarize_attempts
from src.metrics import equity_from_returns, summarize
from src.rp_dual_family import (
    FAMILY_SPECS,
    FAMILY_TICKERS,
    GROUP_LABELS,
    GROUP_ORDER,
    build_rp_dual_family,
    catalog_summary,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "rp_dual_lab.json"
START = "2023-07-01"
RULES = FtmoRules()
ATTEMPT_STEP = 5


def find_daily_kills(
    rets: pd.Series,
    daily_loss: float = 0.05,
    initial: float = 1.0,
) -> list[dict]:
    """
    Days where closed equity breaches FTMO daily loss:
    equity < day_start_balance − (daily_loss × initial).
    """
    r = rets.fillna(0.0)
    eq = float(initial)
    out: list[dict] = []
    limit = daily_loss * initial
    for dt, ret in r.items():
        day_start = eq
        eq = day_start * (1.0 + float(ret))
        day_pnl = eq - day_start
        if eq < day_start - limit - 1e-12:
            out.append({
                "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                "equity": round(float(eq), 6),
                "day_start": round(float(day_start), 6),
                "day_pnl": round(float(day_pnl), 6),
                "day_return": round(float(ret), 6),
            })
    return out


def _curve(
    rets: pd.Series,
    step: int = 2,
    *,
    kill_days: list[dict] | None = None,
) -> list[dict]:
    """Equity curve; always retains FTMO daily-loss kill days when downsampling."""
    eq = equity_from_returns(rets.fillna(0.0))
    kill_dates = {k["date"] for k in (kill_days or [])}
    if step > 1 and len(eq) > step * 2:
        keep = set(range(0, len(eq), step))
        keep.add(len(eq) - 1)
        for i, dt in enumerate(eq.index):
            if pd.Timestamp(dt).strftime("%Y-%m-%d") in kill_dates:
                keep.add(i)
        idxs = sorted(keep)
        eq = eq.iloc[idxs]
    rows = []
    for dt, val in eq.items():
        d = pd.Timestamp(dt).strftime("%Y-%m-%d")
        rows.append({
            "date": d,
            "equity": round(float(val), 6),
            "daily_kill": d in kill_dates,
        })
    return rows


def _slice(rets: pd.Series, end: pd.Timestamp, days: int | None) -> pd.Series:
    if days is None:
        return rets
    return rets.loc[rets.index >= end - pd.Timedelta(days=days)]


def score_row(chal: dict, metrics: dict) -> float:
    fail = float(chal.get("fail_rate") or 0.0)
    pas = float(chal.get("full_pass_rate") or 0.0)
    sharpe = float(metrics.get("sharpe") or 0.0)
    mdd = abs(float(metrics.get("max_dd") or 0.0))
    composite = (
        0.40 * (1.0 - fail)
        + 0.25 * pas
        + 0.25 * min(max(sharpe, -1.0), 2.5) / 2.5
        + 0.10 * (1.0 - min(mdd / 0.10, 1.0))
    )
    if fail > 0.2:
        composite -= 0.15
    if pas < 0.05:
        composite -= 0.05
    return round(float(composite), 4)


def evaluate(rets: pd.Series) -> dict:
    if len(rets) < 20:
        return {
            "challenge": summarize_attempts([]),
            "metrics": summarize(rets, "empty"),
        }
    attempts = rolling_challenges(rets, step=ATTEMPT_STEP, rules=RULES, min_remaining=60)
    return {
        "challenge": summarize_attempts(attempts),
        "metrics": summarize(rets, "book"),
    }


def run() -> dict:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Loading family universe ({len(FAMILY_TICKERS)} tickers)…")
    prices = load_universe(FAMILY_TICKERS, start=START, ffill_limit=5)
    end = prices.index[-1]
    prices = prices.loc[prices.index >= end - pd.Timedelta(days=365 * 2 + 14)]
    print(f"Aligned {prices.shape[0]}d × {prices.shape[1]}  ({prices.index[0].date()} → {prices.index[-1].date()})")

    rows = []
    curves = {}
    curves_6m = {}
    for spec in FAMILY_SPECS:
        print(f"  {spec.id}…")
        rets, diag = build_rp_dual_family(prices, spec)
        rets = rets.reindex(prices.index).fillna(0.0)
        full = evaluate(rets)
        windows = {}
        for wname, days in [("2Y", None), ("6M", 183), ("3M", 92), ("1M", 31)]:
            m = summarize(_slice(rets, end, days), f"{spec.id}:{wname}")
            windows[wname] = {
                "metrics": m,
                "n_days": int(len(_slice(rets, end, days))),
            }
        sc = score_row(full["challenge"], full["metrics"])
        daily = rets.fillna(0.0)
        kills = find_daily_kills(daily, RULES.daily_loss)
        worst_day = float(daily.min()) if len(daily) else 0.0
        eq = equity_from_returns(daily)
        min_eq = float(eq.min()) if len(eq) else 1.0
        row = {
            "id": spec.id,
            "name": spec.name,
            "group": spec.group,
            "sleeve": spec.sleeve,
            "thesis": spec.thesis,
            "n_holdings": diag.get("n_holdings"),
            "n_assets": diag.get("n_assets"),
            "assets": diag.get("assets", []),
            "filters": {
                "min_mcap_b": spec.min_mcap_b,
                "min_ann_vol": spec.min_ann_vol,
                "vol_percentile": spec.vol_percentile,
            },
            "score": sc,
            "full_2y": full,
            "windows": windows,
            "risk": {
                "worst_day": worst_day,
                "daily_headroom": RULES.daily_loss + worst_day,
                "min_equity": min_eq,
                "max_headroom": min_eq - (1.0 - RULES.max_loss),
                "cleared_daily": worst_day > -RULES.daily_loss,
                "cleared_max": min_eq > (1.0 - RULES.max_loss),
                "daily_kill_count": len(kills),
                "daily_kills": kills,
            },
            "curve_key": spec.id,
        }
        rows.append(row)
        curves[spec.id] = _curve(rets, step=3, kill_days=kills)
        kills_6m = [k for k in kills if k["date"] >= (end - pd.Timedelta(days=183)).strftime("%Y-%m-%d")]
        curves_6m[spec.id] = _curve(_slice(rets, end, 183), step=1, kill_days=kills_6m)
        c = full["challenge"]
        print(
            f"    score={sc:.3f} pass={c['full_pass_rate']:.1%} fail={c['fail_rate']:.1%} "
            f"Sharpe={full['metrics']['sharpe']:.2f} assets={diag['n_assets']} n={diag['n_holdings']}"
        )

    # Rank within each group + global
    for g in GROUP_ORDER:
        subset = [r for r in rows if r["group"] == g]
        subset.sort(key=lambda r: r["score"], reverse=True)
        for i, r in enumerate(subset, start=1):
            r["group_rank"] = i
    rows_sorted = sorted(rows, key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(rows_sorted, start=1):
        r["rank"] = i
    # keep group order for page while attaching global rank
    by_id = {r["id"]: r for r in rows_sorted}
    rows = [by_id[s.id] for s in FAMILY_SPECS]

    baseline = by_id.get("rp_dual_base") or rows_sorted[0]
    groups_payload = []
    for g in GROUP_ORDER:
        members = [r for r in rows if r["group"] == g]
        members_sorted = sorted(members, key=lambda r: r["score"], reverse=True)
        groups_payload.append({
            "id": g,
            "label": GROUP_LABELS.get(g, g),
            "count": len(members),
            "best_id": members_sorted[0]["id"] if members_sorted else None,
            "strategy_ids": [m["id"] for m in members],
        })

    # Baseline focus curves with floor + kill markers
    base_rets = build_rp_dual_family(prices, FAMILY_SPECS[0])[0].reindex(prices.index).fillna(0.0)
    base_kills = find_daily_kills(base_rets, RULES.daily_loss)
    focus = {}
    for key, days in [("2Y", None), ("6M", 183), ("3M", 92), ("1M", 31)]:
        sliced = _slice(base_rets, end, days)
        start_d = sliced.index[0].strftime("%Y-%m-%d") if len(sliced) else ""
        k = [x for x in base_kills if x["date"] >= start_d]
        focus[key] = {
            "curve": _curve(sliced, step=1 if days and days <= 183 else 3, kill_days=k),
            "daily_kills": k,
            "daily_kill_count": len(k),
        }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "RP + Dual-mom family research on Yahoo CFD proxies. "
            "Market-cap figures are static approximations for filtering. "
            "FTMO daily 5% / max 10% rules applied in challenge tallies."
        ),
        "how_to_add": (
            "Append a FamilySpec to src/rp_dual_family.py::FAMILY_SPECS "
            "(set group=baseline|sleeve|filter|trade_ladder), then run "
            "`python3 -m src.run_rp_dual_lab`."
        ),
        "rules": {
            "daily_loss": RULES.daily_loss,
            "max_loss": RULES.max_loss,
            "max_loss_floor": 1.0 - RULES.max_loss,
            "phase1_target": RULES.phase1_target,
            "phase2_target": RULES.phase2_target,
        },
        "universe": {
            "start": str(prices.index[0].date()),
            "end": str(prices.index[-1].date()),
            "n_days": int(len(prices)),
            "tickers": FAMILY_TICKERS,
        },
        "catalog": catalog_summary(),
        "groups": groups_payload,
        "baseline_id": baseline["id"],
        "winner_id": rows_sorted[0]["id"],
        "strategies": rows,
        "ranked": [{"id": r["id"], "rank": r["rank"], "score": r["score"]} for r in rows_sorted],
        "baseline_focus_curves": focus,
        "curves": curves,
        "curves_6m": curves_6m,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT} ({len(rows)} strategies)")
    print("Winner:", rows_sorted[0]["name"], rows_sorted[0]["score"])
    print("Baseline:", baseline["name"], baseline["score"])
    return payload


if __name__ == "__main__":
    run()
