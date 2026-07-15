"""
FTMO Challenge lab — multi-strategy bakeoff under 2-Step rules.

Outputs site/data/ftmo_lab.json for site/ftmo-lab.html.

Focus:
  1) Pass challenge with least failure likelihood
  2) Consistent gains after / during the path
  Windows: 2Y full + emphasis on trailing 6M / 3M / 1M
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.data import load_universe
from src.ftmo_rules import FtmoRules, rolling_challenges, summarize_attempts, simulate_challenge
from src.ftmo_strategies import FTMO_TICKERS, STRATEGY_BUILDERS, STRATEGY_META
from src.metrics import equity_from_returns, summarize

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "ftmo_lab.json"

# Emphasize recent regime; still score full ~2Y path for attempt counts
START = "2023-07-01"
RULES = FtmoRules()
ATTEMPT_STEP = 5


def _curve(rets: pd.Series, step: int = 1) -> list[dict]:
    eq = equity_from_returns(rets.fillna(0.0))
    if step > 1 and len(eq) > step * 2:
        idxs = list(range(0, len(eq), step))
        if idxs[-1] != len(eq) - 1:
            idxs.append(len(eq) - 1)
        eq = eq.iloc[idxs]
    return [{"date": dt.strftime("%Y-%m-%d"), "equity": round(float(v), 6)} for dt, v in eq.items()]


def _slice_rets(rets: pd.Series, end: pd.Timestamp, calendar_days: int | None) -> pd.Series:
    if calendar_days is None:
        return rets
    start = end - pd.Timedelta(days=calendar_days)
    return rets.loc[(rets.index >= start) & (rets.index <= end)]


def score_strategy(chal: dict, metrics: dict, recent: dict) -> dict:
    """
    Composite for FTMO goals (fail-first):
      1) Fail least often
      2) Still pass (not endless timeout)
      3) Consistent return
      4) Room to improve = safe but not maxed return
    """
    fail_rate = float(chal["fail_rate"]) if "fail_rate" in chal else 1.0
    pass_rate = float(chal["full_pass_rate"]) if "full_pass_rate" in chal else 0.0
    p1_rate = float(chal["phase1_pass_rate"]) if "phase1_pass_rate" in chal else 0.0
    room = chal.get("avg_room_on_pass")
    room_score = float(room) if room is not None else 0.0

    sharpe = float(metrics.get("sharpe") or 0.0)
    cagr = float(metrics.get("cagr") or 0.0)
    mdd = abs(float(metrics.get("max_dd") or 0.0))
    sortino = float(metrics.get("sortino") or 0.0)

    # Recent windows: ignore empty (all-censored) windows so they don't zero the score
    recent_used = []
    for w in ("6M", "3M", "1M"):
        ch = recent[w]["chal"]
        if int(ch.get("n_attempts") or 0) > 0:
            recent_used.append(recent[w])
    if recent_used:
        r_pass = float(np.mean([x["chal"]["full_pass_rate"] for x in recent_used]))
        r_fail = float(np.mean([x["chal"]["fail_rate"] for x in recent_used]))
    else:
        r_pass, r_fail = pass_rate, fail_rate
    r_sharpe = float(np.mean([recent[w]["metrics"]["sharpe"] for w in ("6M", "3M", "1M")]))
    r_ret = float(np.mean([recent[w]["metrics"]["total_return"] for w in ("6M", "3M", "1M")]))

    continuous_ok = mdd <= 0.12

    # Fail-first survival — a 0% fail / decent pass book beats a high-pass / high-fail book
    survival = (
        0.40 * (1.0 - fail_rate)
        + 0.18 * pass_rate
        + 0.10 * p1_rate
        + 0.14 * (1.0 - r_fail)
        + 0.08 * r_pass
        + 0.06 * min(max(room_score, 0.0), 0.15) / 0.15
        + 0.04 * min(max(sharpe, -1.0), 2.5) / 2.5
    )

    ret_util = min(max(cagr, 0.0), 0.25) / 0.25
    # Only credit "room to improve" when the book is actually safe
    safety_gate = max(0.0, 1.0 - fail_rate / 0.20)  # zero credit above 20% fail
    improvement_room = safety_gate * (
        0.40 * (1.0 - fail_rate)
        + 0.25 * min(max(pass_rate, 0.0), 1.0)
        + 0.20 * min(max(room_score, 0.0), 0.15) / 0.15
        + 0.15 * (1.0 - ret_util)
    )

    return_score = (
        0.32 * min(max(sharpe, -1.0), 3.0) / 3.0
        + 0.22 * min(max(sortino, -1.0), 3.0) / 3.0
        + 0.18 * min(max(r_ret, -0.2), 0.4) / 0.4
        + 0.12 * min(max(cagr, -0.2), 0.4) / 0.4
        + 0.10 * pass_rate
        + 0.06 * (1.0 - fail_rate)
    )

    composite = 0.60 * survival + 0.25 * return_score + 0.15 * improvement_room
    if not continuous_ok:
        composite -= 0.12
    if fail_rate > 0.20:
        composite -= 0.15
    if fail_rate > 0.35:
        composite -= 0.10
    # Tiny pass rate with many timeouts is not a winning challenge plan
    if pass_rate < 0.05:
        composite -= 0.08
    if pass_rate < 0.05 and fail_rate < 0.05:
        composite -= 0.04
    # Penalize books that never clear Phase 1 even if "safe"
    if p1_rate < 0.10:
        composite -= 0.06

    return {
        "survival_score": round(float(survival), 4),
        "return_score": round(float(return_score), 4),
        "improvement_room": round(float(improvement_room), 4),
        "composite": round(float(composite), 4),
        "recent_pass_avg": round(float(r_pass), 4),
        "recent_fail_avg": round(float(r_fail), 4),
        "recent_sharpe_avg": round(float(r_sharpe), 4),
        "continuous_dd_ok": continuous_ok,
    }


def _phase_result_dict(p) -> dict | None:
    if p is None:
        return None
    return {
        "status": p.status,
        "days": p.days,
        "trading_days": p.trading_days,
        "end_equity": round(p.end_equity, 6),
        "min_equity": round(p.min_equity, 6),
        "room_to_floor": round(p.room_to_floor, 6),
        "hit_target_day": p.hit_target_day,
    }


def evaluate_window(rets: pd.Series, label: str) -> dict:
    if len(rets) < 15:
        empty = summarize_attempts([])
        m = summarize(rets, label)
        return {"chal": empty, "metrics": m, "n_days": int(len(rets)), "single_shot": None, "path_breaches": None}

    n = len(rets)
    # Short focus windows cannot finish a full 252+180 day 2-step — use paced rules.
    if n < 100:
        rules = FtmoRules(max_days_phase1=max(40, n - 5), max_days_phase2=max(25, n // 3))
        min_rem = 12
        step = 3
    elif n < 160:
        rules = FtmoRules(max_days_phase1=90, max_days_phase2=55)
        min_rem = 25
        step = 4
    else:
        rules = RULES
        min_rem = 80 if n >= 200 else 40
        step = ATTEMPT_STEP

    attempts = rolling_challenges(rets, step=step, rules=rules, min_remaining=min_rem)
    chal = summarize_attempts(attempts)
    m = summarize(rets, label)

    shot = simulate_challenge(rets, 0, rules)
    single = {
        "status": shot.status,
        "fail_reason": shot.fail_reason,
        "start": shot.start,
        "phase1": _phase_result_dict(shot.phase1),
        "phase2": _phase_result_dict(shot.phase2),
    }

    eq = 1.0
    floor = 1.0 - rules.max_loss
    daily_hits = 0
    max_hit = False
    min_eq = 1.0
    for r in rets.fillna(0.0):
        day_start = eq
        eq *= 1.0 + float(r)
        min_eq = min(min_eq, eq)
        if eq < day_start - rules.daily_loss:
            daily_hits += 1
        if eq < floor:
            max_hit = True
            break

    return {
        "chal": chal,
        "metrics": m,
        "n_days": int(n),
        "rules_max_p1": rules.max_days_phase1,
        "single_shot": single,
        "path_breaches": {
            "daily_loss_events": daily_hits,
            "max_loss_breach": max_hit,
            "min_equity": round(float(min_eq), 6),
        },
    }


def run() -> dict:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    print(f"Loading FTMO proxy universe ({len(FTMO_TICKERS)} tickers) from {START}…")
    # FX has weekend gaps — allow longer ffill
    prices = load_universe(FTMO_TICKERS, start=START, ffill_limit=5)
    end = prices.index[-1]
    # Restrict primary analysis to ~2Y
    two_y_start = end - pd.Timedelta(days=365 * 2 + 14)
    prices = prices.loc[prices.index >= two_y_start]
    print(f"Aligned prices: {prices.shape[0]} days × {prices.shape[1]} assets  ({prices.index[0].date()} → {prices.index[-1].date()})")

    rows = []
    curves = {}
    window_specs = {
        "2Y": None,
        "6M": 183,
        "3M": 92,
        "1M": 31,
    }

    for sid, builder in STRATEGY_BUILDERS.items():
        print(f"  building {sid}…")
        rets = builder(prices).reindex(prices.index).fillna(0.0)
        meta = STRATEGY_META[sid]

        recent = {}
        for wname, days in window_specs.items():
            sliced = _slice_rets(rets, end, days)
            recent[wname] = evaluate_window(sliced, f"{sid}:{wname}")

        full = recent["2Y"]
        scores = score_strategy(full["chal"], full["metrics"], recent)

        # Improvement narrative
        headroom = full["chal"].get("avg_room_on_pass")
        fail_n = full["chal"]["fails"]
        row = {
            "id": sid,
            "name": meta.name,
            "family": meta.family,
            "thesis": meta.thesis,
            "markets": meta.markets,
            "scores": scores,
            "full_2y": {
                "metrics": full["metrics"],
                "challenge": full["chal"],
            },
            "windows": {
                w: {
                    "metrics": recent[w]["metrics"],
                    "challenge": recent[w]["chal"],
                    "n_days": recent[w]["n_days"],
                    "single_shot": recent[w].get("single_shot"),
                    "path_breaches": recent[w].get("path_breaches"),
                }
                for w in ("6M", "3M", "1M", "2Y")
            },
            "fails_total_2y": fail_n,
            "room_on_pass": headroom,
            "curve_key": sid,
        }
        rows.append(row)
        # denser curve for 6M focus chart; full 2Y downsampled
        curves[sid] = _curve(rets, step=3)
        curves[f"{sid}__6m"] = _curve(_slice_rets(rets, end, 183), step=1)
        print(
            f"    2Y pass={full['chal']['full_pass_rate']:.1%} fail={full['chal']['fail_rate']:.1%} "
            f"Sharpe={full['metrics']['sharpe']:.2f} composite={scores['composite']:.3f}"
        )

    rows.sort(key=lambda r: r["scores"]["composite"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i

    winner = rows[0]
    safe = [r for r in rows if r["full_2y"]["challenge"]["fail_rate"] <= 0.05]
    least_fail = min(
        rows,
        key=lambda r: (
            r["full_2y"]["challenge"]["fail_rate"],
            -r["full_2y"]["challenge"]["full_pass_rate"],
            -r["scores"]["composite"],
        ),
    )
    best_return = max(
        rows,
        key=lambda r: (r["scores"]["return_score"], -r["full_2y"]["challenge"]["fail_rate"]),
    )
    improvable_pool = [
        r
        for r in safe
        if r["full_2y"]["challenge"]["full_pass_rate"] >= 0.10
    ] or [
        r
        for r in rows
        if r["full_2y"]["challenge"]["fail_rate"] <= 0.15
        and r["full_2y"]["challenge"]["full_pass_rate"] >= 0.15
    ] or safe or rows
    most_improvable = max(improvable_pool, key=lambda r: r["scores"]["improvement_room"])

    # Winner recent window curves for UI
    winner_rets = STRATEGY_BUILDERS[winner["id"]](prices).reindex(prices.index).fillna(0.0)
    focus_curves = {
        "2Y": _curve(winner_rets, step=3),
        "6M": _curve(_slice_rets(winner_rets, end, 183), step=1),
        "3M": _curve(_slice_rets(winner_rets, end, 92), step=1),
        "1M": _curve(_slice_rets(winner_rets, end, 31), step=1),
    }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Research approximation using Yahoo daily proxies for FTMO CFDs (FX, indices, metals, crypto, stocks). "
            "Not identical to FTMO fills, swaps, commissions, or intraday equity marks. "
            "Verify current FTMO Trading Objectives before any challenge purchase."
        ),
        "rules": {
            "program": "FTMO Challenge 2-Step (classic)",
            "phase1_target": RULES.phase1_target,
            "phase2_target": RULES.phase2_target,
            "daily_loss": RULES.daily_loss,
            "max_loss_static": RULES.max_loss,
            "min_trading_days": RULES.min_trading_days,
            "sim_max_days_phase1": RULES.max_days_phase1,
            "sim_max_days_phase2": RULES.max_days_phase2,
            "attempt_step_days": ATTEMPT_STEP,
            "notes": [
                "Each rolling start is an independent Challenge → Verification attempt.",
                "Phase 2 resets to a fresh 1.0 equity Verification account.",
                "Daily loss uses closed-day PnL vs day-start balance − 5% initial (no intraday path).",
                "Fail tallies count daily-loss and max-loss breaches; timeouts are separate (not failures).",
            ],
        },
        "universe": {
            "start": str(prices.index[0].date()),
            "end": str(prices.index[-1].date()),
            "n_days": int(len(prices)),
            "tickers": FTMO_TICKERS,
            "groups": {
                "fx": [t for t in FTMO_TICKERS if t.endswith("=X")],
                "indices": ["SPY", "QQQ", "DIA", "IWM"],
                "commod": ["GLD", "SLV", "USO"],
                "crypto": ["BTC-USD", "ETH-USD"],
                "stock_cfd": [t for t in FTMO_TICKERS if t.isalpha() and t not in ("SPY", "QQQ", "DIA", "IWM", "GLD", "SLV", "USO")],
            },
        },
        "ranking_rubric": {
            "survival": "Low fail rate + high full/phase1 pass rates (2Y + recent windows)",
            "return": "Sharpe / Sortino / CAGR + recent total returns",
            "improvement_room": "Safe (low fail, cushion above 90% floor) but not yet maxing return — worth iterating",
            "composite": "0.60 survival (fail-first) + 0.25 return + 0.15 improvement",
        },
        "champions": {
            "overall": {
                "id": winner["id"],
                "name": winner["name"],
                "why": (
                    f"Best composite ({winner['scores']['composite']}). "
                    f"2Y fail rate {winner['full_2y']['challenge']['fail_rate']:.1%}, "
                    f"full-pass {winner['full_2y']['challenge']['full_pass_rate']:.1%}, "
                    f"Sharpe {winner['full_2y']['metrics']['sharpe']:.2f}."
                ),
            },
            "least_fails": {
                "id": least_fail["id"],
                "name": least_fail["name"],
                "fail_rate": least_fail["full_2y"]["challenge"]["fail_rate"],
                "fails": least_fail["full_2y"]["challenge"]["fails"],
                "attempts": least_fail["full_2y"]["challenge"]["n_attempts"],
            },
            "best_return": {
                "id": best_return["id"],
                "name": best_return["name"],
                "return_score": best_return["scores"]["return_score"],
                "sharpe": best_return["full_2y"]["metrics"]["sharpe"],
                "cagr": best_return["full_2y"]["metrics"]["cagr"],
            },
            "most_room_to_improve": {
                "id": most_improvable["id"],
                "name": most_improvable["name"],
                "improvement_room": most_improvable["scores"]["improvement_room"],
                "note": "Highest safety cushion relative to extracted return — best candidate to carefully lever up.",
            },
        },
        "strategies": rows,
        "winner_focus_curves": focus_curves,
        "curves": {r["id"]: curves[r["id"]] for r in rows},
        "curves_6m": {r["id"]: curves[f"{r['id']}__6m"] for r in rows},
        "playbook": {
            "recommended": winner["id"],
            "challenge_ops": [
                "Trade FTMO Swing if you hold overnight across weekends on FX/indices.",
                "Keep modeled daily loss well under 5% — our brake soft-stops near 1–2% closed-day loss.",
                "Do not chase Phase-1 10% with crypto size; use crypto only as a dampened sleeve if at all.",
                "Min 4 trading days — grind strategies naturally satisfy this; avoid one-shot lottery days.",
                "After a −1% day, cut exposure (agent brake) rather than revenge-trading.",
                "Prefer static 2-Step over 1-Step trailing DD for these books.",
            ],
            "improvement_levers": [
                "Raise vol target slowly (0.5% increments) only while rolling fail rate stays <10%.",
                "Add session filters (skip high-impact USD news windows) before increasing size.",
                "Walk-forward re-fit lookbacks quarterly; freeze during a live challenge.",
            ],
        },
    }

    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT}")
    print(
        "Winner:",
        winner["rank"],
        winner["name"],
        f"composite={winner['scores']['composite']}",
        f"fail={winner['full_2y']['challenge']['fail_rate']:.1%}",
    )
    print(
        "Least fails:",
        least_fail["name"],
        f"fail={least_fail['full_2y']['challenge']['fail_rate']:.1%}",
    )
    print(
        "Best return:",
        best_return["name"],
        f"Sharpe={best_return['full_2y']['metrics']['sharpe']:.2f}",
    )
    print(
        "Most improvable:",
        most_improvable["name"],
        f"room={most_improvable['scores']['improvement_room']:.3f}",
    )
    return payload


if __name__ == "__main__":
    run()
