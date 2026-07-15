"""
Prop-account lab — multi-strategy bakeoff under dollar account rules.

Account model (user):
  $25,000 start · $1,250 fixed daily loss · $5,000 max loss from start
  Withdraw ALL day profit every day (cushion does not rebuild from wins)

Outputs site/data/ftmo_lab.json for site/ftmo-lab.html.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.data import load_universe
from src.ftmo_rules import (
    FtmoRules,
    PayoutPolicy,
    dollars,
    rolling_challenges,
    rolling_funded,
    summarize_attempts,
    summarize_funded,
    simulate_challenge,
    walk_daily_withdraw,
)
from src.ftmo_strategies import FTMO_TICKERS, STRATEGY_BUILDERS, STRATEGY_META
from src.metrics import summarize

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "ftmo_lab.json"

# Emphasize recent regime; still score full ~2Y path for attempt counts
START = "2023-07-01"
RULES = FtmoRules()
ATTEMPT_STEP = 5
# Living policy: withdraw all day profit every closed day.
PAYOUT = PayoutPolicy(
    every_n_days=1,
    min_profit=0.0,
    keep_buffer=0.0,
    trader_split=0.80,
    max_days=252,
    mode="day_pnl",
)
FUNDED_STEP = 10


def _curve(rets: pd.Series, step: int = 1, *, daily_loss: float | None = None) -> list[dict]:
    """Equity under daily profit-withdraw; marks kill days ($1,250 daily or $5k max)."""
    del daily_loss  # limits come from RULES
    r = rets.fillna(0.0)
    eq, kills, _locked, locked_s = walk_daily_withdraw(r, RULES)
    kill_set = {k["date"] for k in kills}
    if step > 1 and len(eq) > step * 2:
        keep = set(range(0, len(eq), step))
        keep.add(len(eq) - 1)
        for i, dt in enumerate(eq.index):
            if pd.Timestamp(dt).strftime("%Y-%m-%d") in kill_set:
                keep.add(i)
        idxs = sorted(keep)
        eq = eq.iloc[idxs]
        locked_s = locked_s.reindex(eq.index)
    return [
        {
            "date": dt.strftime("%Y-%m-%d"),
            "equity": round(float(val), 6),
            "equity_dollars": round(dollars(val, RULES), 2),
            "profit_tally": round(float(locked_s.loc[dt]), 6),
            "profit_tally_dollars": round(dollars(float(locked_s.loc[dt]), RULES), 2),
            "total_dollars": round(
                dollars(float(val), RULES) + dollars(float(locked_s.loc[dt]), RULES), 2
            ),
            "daily_kill": dt.strftime("%Y-%m-%d") in kill_set,
        }
        for dt, val in eq.items()
    ]


def _slice_rets(rets: pd.Series, end: pd.Timestamp, calendar_days: int | None) -> pd.Series:
    if calendar_days is None:
        return rets
    start = end - pd.Timedelta(days=calendar_days)
    return rets.loc[(rets.index >= start) & (rets.index <= end)]


def score_strategy(chal: dict, metrics: dict, recent: dict, funded: dict, hoard: dict) -> dict:
    """
    Composite for FTMO goals (fail-first + paycheck discipline):
      1) Fail least often (challenge + funded breach)
      2) Still pass challenge
      3) Lock consistent payouts (breach must not eat the stack)
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

    continuous_ok = mdd <= RULES.max_loss + 0.02

    fund_breach = float(funded.get("breach_rate") or 0.0)
    locked = float(funded.get("avg_locked_trader") or 0.0)
    lost = float(funded.get("avg_unpaid_lost") or 0.0)
    pay_hit = float(funded.get("payout_hit_rate") or 0.0)
    n_pay = float(funded.get("avg_n_payouts") or 0.0)
    net = float(funded.get("net_kept_vs_lost") or 0.0)
    hoard_lost = float(hoard.get("avg_unpaid_lost") or 0.0)
    payout_edge = max(0.0, hoard_lost - lost)

    survival = (
        0.32 * (1.0 - fail_rate)
        + 0.14 * (1.0 - fund_breach)
        + 0.14 * pass_rate
        + 0.08 * p1_rate
        + 0.10 * (1.0 - r_fail)
        + 0.06 * r_pass
        + 0.05 * min(max(room_score, 0.0), 0.15) / 0.15
        + 0.04 * min(max(sharpe, -1.0), 2.5) / 2.5
        + 0.07 * min(pay_hit, 1.0)
    )

    ret_util = min(max(cagr, 0.0), 0.25) / 0.25
    safety_gate = max(0.0, 1.0 - fail_rate / 0.20)
    improvement_room = safety_gate * (
        0.35 * (1.0 - fail_rate)
        + 0.20 * (1.0 - fund_breach)
        + 0.20 * min(max(pass_rate, 0.0), 1.0)
        + 0.15 * min(max(room_score, 0.0), 0.15) / 0.15
        + 0.10 * (1.0 - ret_util)
    )

    return_score = (
        0.22 * min(max(sharpe, -1.0), 3.0) / 3.0
        + 0.14 * min(max(sortino, -1.0), 3.0) / 3.0
        + 0.12 * min(max(r_ret, -0.2), 0.4) / 0.4
        + 0.08 * min(max(cagr, -0.2), 0.4) / 0.4
        + 0.08 * pass_rate
        + 0.06 * (1.0 - fail_rate)
        + 0.18 * min(max(locked, 0.0), 0.25) / 0.25
        + 0.08 * min(max(net, -0.05), 0.25) / 0.25
        + 0.04 * min(n_pay / 12.0, 1.0)
    )

    payout_score = (
        0.35 * min(max(locked, 0.0), 0.25) / 0.25
        + 0.20 * (1.0 - fund_breach)
        + 0.15 * pay_hit
        + 0.15 * min(max(payout_edge, 0.0), 0.15) / 0.15
        + 0.10 * (1.0 - min(lost / 0.05, 1.0))
        + 0.05 * min(n_pay / 12.0, 1.0)
    )

    composite = (
        0.45 * survival
        + 0.25 * payout_score
        + 0.20 * return_score
        + 0.10 * improvement_room
    )
    if not continuous_ok:
        composite -= 0.12
    if fail_rate > 0.20:
        composite -= 0.15
    if fail_rate > 0.35:
        composite -= 0.10
    if fund_breach > 0.25:
        composite -= 0.08
    if pass_rate < 0.05:
        composite -= 0.08
    if pass_rate < 0.05 and fail_rate < 0.05:
        composite -= 0.04
    if p1_rate < 0.10:
        composite -= 0.06

    return {
        "survival_score": round(float(survival), 4),
        "return_score": round(float(return_score), 4),
        "improvement_room": round(float(improvement_room), 4),
        "payout_score": round(float(payout_score), 4),
        "composite": round(float(composite), 4),
        "recent_pass_avg": round(float(r_pass), 4),
        "recent_fail_avg": round(float(r_fail), 4),
        "recent_sharpe_avg": round(float(r_sharpe), 4),
        "continuous_dd_ok": continuous_ok,
        "avg_locked_trader": round(locked, 4),
        "avg_unpaid_lost": round(lost, 4),
        "fund_breach_rate": round(fund_breach, 4),
        "payout_edge_vs_hoard": round(float(payout_edge), 4),
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

    eq, kills, _locked, _locked_s = walk_daily_withdraw(rets.fillna(0.0), rules)
    daily_hits = sum(1 for k in kills if k.get("daily_kill"))
    max_hit = any(k.get("max_kill") for k in kills)
    min_eq = float(eq.min()) if len(eq) else 1.0

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
            "min_equity_dollars": round(dollars(min_eq, rules), 2),
        },
    }



def build_risk_visuals(rets: pd.Series, strategies: list[dict], rules: FtmoRules) -> dict:
    """Dollar-limit envelope: $1,250 daily / $5k max, daily profit withdraw."""
    r = rets.fillna(0.0)
    eq, kills_all, locked, locked_s = walk_daily_withdraw(r, rules)
    daily = r.astype(float)
    worst_day = float(daily.min()) if len(daily) else 0.0
    best_day = float(daily.max()) if len(daily) else 0.0
    worst_day_dollars = worst_day * rules.initial_balance
    daily_headroom = rules.daily_loss + worst_day
    min_eq = float(eq.min()) if len(eq) else 1.0
    max_floor = rules.max_loss_floor
    max_headroom = min_eq - max_floor
    daily_kill_dates = {k["date"] for k in kills_all}

    def path_pack(series: pd.Series, step: int = 1) -> dict:
        s = series.fillna(0.0)
        e, kills, _locked, locked_path = walk_daily_withdraw(s, rules)
        kill_set = {k["date"] for k in kills}
        if step > 1 and len(e) > step * 2:
            keep = set(range(0, len(e), step))
            keep.add(len(e) - 1)
            for i, dt in enumerate(e.index):
                if pd.Timestamp(dt).strftime("%Y-%m-%d") in kill_set:
                    keep.add(i)
            idxs = sorted(keep)
            e = e.iloc[idxs]
            locked_path = locked_path.reindex(e.index)
            s = s.reindex(e.index).fillna(0.0)
        dates = [dt.strftime("%Y-%m-%d") for dt in e.index]
        profit = [round(float(v), 6) for v in locked_path.values]
        profit_d = [round(dollars(v, rules), 2) for v in locked_path.values]
        eq_d = [round(dollars(v, rules), 2) for v in e.values]
        return {
            "dates": dates,
            "equity": [round(float(v), 6) for v in e.values],
            "equity_dollars": eq_d,
            "profit_tally": profit,
            "profit_tally_dollars": profit_d,
            "total_dollars": [round(a + b, 2) for a, b in zip(eq_d, profit_d)],
            "daily": [round(float(v), 6) for v in s.values],
            "daily_dollars": [round(float(v) * rules.initial_balance, 2) for v in s.values],
            "daily_kill": [d in kill_set for d in dates],
            "daily_kills": [
                {
                    "date": d,
                    "equity": round(float(e.loc[pd.Timestamp(d)]), 6),
                    "equity_dollars": round(dollars(float(e.loc[pd.Timestamp(d)]), rules), 2),
                    "profit_tally_dollars": round(dollars(float(locked_path.loc[pd.Timestamp(d)]), rules), 2),
                }
                for d in dates
                if d in kill_set
            ],
            "daily_kill_count": int(sum(1 for d in dates if d in kill_set)),
            "final_profit_tally_dollars": profit_d[-1] if profit_d else 0.0,
            "max_loss_floor": [round(max_floor, 6)] * len(e),
            "max_loss_floor_dollars": [round(rules.max_loss_floor_dollars, 2)] * len(e),
            "daily_loss_limit": [-rules.daily_loss] * len(e),
            "daily_loss_limit_dollars": [-rules.daily_loss_dollars] * len(e),
            "daily_gain_ref": [rules.daily_loss] * len(e),
            "daily_gain_ref_dollars": [rules.daily_loss_dollars] * len(e),
        }

    end = r.index[-1]
    # Breach board for bar chart
    breach_board = []
    for s in strategies:
        c = s["full_2y"]["challenge"]
        m = s["full_2y"]["metrics"]
        breach_board.append({
            "id": s["id"],
            "name": s["name"],
            "rank": s["rank"],
            "fail_daily": c["fail_daily"],
            "fail_max": c["fail_max"],
            "fails": c["fails"],
            "attempts": c["n_attempts"],
            "fail_rate": c["fail_rate"],
            "max_dd": m["max_dd"],
            "min_equity_phase1": c.get("avg_min_equity_phase1"),
            "room_to_floor": (c.get("avg_min_equity_phase1") or 1.0) - max_floor if c.get("avg_min_equity_phase1") is not None else None,
            "cleared_max_dd_gate": abs(float(m.get("max_dd") or 0.0)) < rules.max_loss,
        })

    # Histogram of daily returns for winner (bins)
    bins = np.linspace(-0.08, 0.08, 25)
    hist, edges = np.histogram(daily.clip(-0.08, 0.08), bins=bins)
    hist_pack = {
        "centers": [round(float((edges[i] + edges[i + 1]) / 2), 5) for i in range(len(hist))],
        "centers_dollars": [
            round(float((edges[i] + edges[i + 1]) / 2) * rules.initial_balance, 2)
            for i in range(len(hist))
        ],
        "counts": [int(x) for x in hist],
        "daily_limit": -rules.daily_loss,
        "daily_limit_dollars": -rules.daily_loss_dollars,
    }

    return {
        "limits": {
            "initial_balance": rules.initial_balance,
            "daily_loss": rules.daily_loss,
            "daily_loss_dollars": rules.daily_loss_dollars,
            "max_loss": rules.max_loss,
            "max_loss_dollars": rules.max_loss_dollars,
            "max_loss_floor": max_floor,
            "max_loss_floor_dollars": rules.max_loss_floor_dollars,
            "phase1_target": rules.phase1_target,
            "phase2_target": rules.phase2_target,
            "withdraw_profits_daily": True,
        },
        "winner_envelope": {
            "worst_day": worst_day,
            "worst_day_dollars": round(worst_day_dollars, 2),
            "best_day": best_day,
            "best_day_dollars": round(best_day * rules.initial_balance, 2),
            "daily_headroom": daily_headroom,
            "daily_headroom_dollars": round(rules.daily_loss_dollars + worst_day_dollars, 2),
            "min_equity": min_eq,
            "min_equity_dollars": round(dollars(min_eq, rules), 2),
            "max_headroom": max_headroom,
            "max_headroom_dollars": round(dollars(max_headroom, rules), 2),
            "path_max_dd": float((eq / eq.cummax() - 1.0).min()) if len(eq) else 0.0,
            "locked_profit_dollars": round(dollars(locked, rules), 2),
            "daily_kill_count": len(daily_kill_dates),
            "pct_days_worse_than_2pct": float((daily <= -0.02).mean()) if len(daily) else 0.0,
            "pct_days_worse_than_3pct": float((daily <= -0.03).mean()) if len(daily) else 0.0,
            "days_within_1pct_of_daily_limit": int(
                ((daily * rules.initial_balance <= -1000) & (daily * rules.initial_balance > -1250)).sum()
            ),
            "days_at_or_over_daily_limit": int(
                (daily * rules.initial_balance <= -rules.daily_loss_dollars).sum()
            ),
            "cleared_daily_limit": bool(worst_day_dollars > -rules.daily_loss_dollars + 1e-9),
            "cleared_max_floor": bool(min_eq > max_floor + 1e-12),
        },
        "winner_path_2y": path_pack(r, step=3),
        "winner_path_6m": path_pack(r.loc[r.index >= end - pd.Timedelta(days=183)], step=1),
        "daily_hist": hist_pack,
        "breach_board": breach_board,
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
        # Funded phase: assume we pay ourselves out every ~10 trading days (≥1% open profit).
        # Breach burns only unpaid open PnL; locked withdrawals survive.
        funded_paths = rolling_funded(
            rets, step=FUNDED_STEP, rules=RULES, policy=PAYOUT, min_remaining=40, mode="payout"
        )
        hoard_paths = rolling_funded(
            rets, step=FUNDED_STEP, rules=RULES, policy=PAYOUT, min_remaining=40, mode="hoard"
        )
        funded = summarize_funded(funded_paths)
        hoard = summarize_funded(hoard_paths)
        scores = score_strategy(full["chal"], full["metrics"], recent, funded, hoard)

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
                "funded_payout": funded,
                "funded_hoard": hoard,
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
            f"fundBreach={funded['breach_rate']:.1%} locked={funded['avg_locked_trader']:.1%} "
            f"lostOpen={funded['avg_unpaid_lost']:.2%} Sharpe={full['metrics']['sharpe']:.2f} "
            f"composite={scores['composite']:.3f}"
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
    pay_safe = [
        r for r in rows if r["full_2y"]["funded_payout"]["breach_rate"] <= 0.05
    ] or rows
    best_paycheck = max(
        pay_safe,
        key=lambda r: (
            r["full_2y"]["funded_payout"]["avg_locked_trader"],
            r["scores"].get("payout_score", 0.0),
            -r["full_2y"]["funded_payout"]["breach_rate"],
        ),
    )

    # Winner recent window curves for UI
    winner_rets = STRATEGY_BUILDERS[winner["id"]](prices).reindex(prices.index).fillna(0.0)
    focus_curves = {
        "2Y": _curve(winner_rets, step=3, daily_loss=RULES.daily_loss),
        "6M": _curve(_slice_rets(winner_rets, end, 183), step=1, daily_loss=RULES.daily_loss),
        "3M": _curve(_slice_rets(winner_rets, end, 92), step=1, daily_loss=RULES.daily_loss),
        "1M": _curve(_slice_rets(winner_rets, end, 31), step=1, daily_loss=RULES.daily_loss),
    }
    risk_visuals = build_risk_visuals(winner_rets, rows, RULES)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            f"Research model: ${RULES.initial_balance:,.0f} account, fixed "
            f"${RULES.daily_loss_dollars:,.0f} daily loss, "
            f"${RULES.max_loss_dollars:,.0f} max loss from start "
            f"(floor ${RULES.max_loss_floor_dollars:,.0f}), withdraw ALL day profit every day. "
            "Yahoo daily proxies ≠ live fills/swaps/intraday marks."
        ),
        "rules": {
            "program": "$25k prop account · fixed-dollar DLL + static max loss",
            "initial_balance": RULES.initial_balance,
            "daily_loss_dollars": RULES.daily_loss_dollars,
            "max_loss_dollars": RULES.max_loss_dollars,
            "max_loss_floor_dollars": RULES.max_loss_floor_dollars,
            "phase1_target": RULES.phase1_target,
            "phase2_target": RULES.phase2_target,
            "daily_loss": RULES.daily_loss,
            "max_loss_static": RULES.max_loss,
            "max_loss_floor": RULES.max_loss_floor,
            "withdraw_profits_daily": True,
            "min_trading_days": RULES.min_trading_days,
            "sim_max_days_phase1": RULES.max_days_phase1,
            "sim_max_days_phase2": RULES.max_days_phase2,
            "attempt_step_days": ATTEMPT_STEP,
            "notes": [
                f"Daily loss is a fixed ${RULES.daily_loss_dollars:,.0f} from day-start — not a % of current equity.",
                f"Max loss is ${RULES.max_loss_dollars:,.0f} from the ${RULES.initial_balance:,.0f} start (floor ${RULES.max_loss_floor_dollars:,.0f}).",
                "Every green day: withdraw 100% of that day's profit; equity only ratchets down on losses.",
                "Challenge phases still require equity growth (no mid-phase withdraw) so pass rates stay measurable.",
                "Kill × markers use the funded daily-withdraw path.",
                "Fail tallies count daily-loss and max-loss breaches; timeouts are separate.",
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
            "survival": "Low challenge fail + low funded breach + pass rates",
            "payout": "Locked trader payouts under biweekly pay-yourself-out; unpaid lost on breach stays small",
            "return": "Sharpe / Sortino / CAGR + locked paycheck yield",
            "improvement_room": "Safe but not maxed — worth carefully leveraging",
            "composite": "0.45 survival + 0.25 payout + 0.20 return + 0.10 improvement",
        },
        "payout_policy": {
            "assumption": "Withdraw ALL day profit every closed day — cushion never rebuilds from wins after a drawdown.",
            "every_n_trading_days": PAYOUT.every_n_days,
            "min_open_profit": PAYOUT.min_profit,
            "keep_buffer": PAYOUT.keep_buffer,
            "trader_split": PAYOUT.trader_split,
            "mode": PAYOUT.mode,
            "funded_horizon_days": PAYOUT.max_days,
            "contrast": "Hoard mode never withdraws until end/breach — contrast for unpaid-tower risk.",
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
            "best_paycheck": {
                "id": best_paycheck["id"],
                "name": best_paycheck["name"],
                "payout_score": best_paycheck["scores"].get("payout_score"),
                "avg_locked_trader": best_paycheck["full_2y"]["funded_payout"]["avg_locked_trader"],
                "fund_breach_rate": best_paycheck["full_2y"]["funded_payout"]["breach_rate"],
                "avg_unpaid_lost": best_paycheck["full_2y"]["funded_payout"]["avg_unpaid_lost"],
                "hoard_unpaid_lost": best_paycheck["full_2y"]["funded_hoard"]["avg_unpaid_lost"],
                "note": "Best locked payout stream under the pay-yourself-out policy (80% trader split).",
            },
        },
        "strategies": rows,
        "winner_focus_curves": focus_curves,
        "risk_visuals": risk_visuals,
        "curves": {r["id"]: curves[r["id"]] for r in rows},
        "curves_6m": {r["id"]: curves[f"{r['id']}__6m"] for r in rows},
        "playbook": {
            "recommended": winner["id"],
            "challenge_ops": [
                f"Hard stop before −${RULES.daily_loss_dollars:,.0f} day PnL on the ${RULES.initial_balance:,.0f} account.",
                f"Never let equity pierce ${RULES.max_loss_floor_dollars:,.0f} (max −${RULES.max_loss_dollars:,.0f} from start).",
                "Challenge phases still need equity in-account to hit +10% / +5% (sim only).",
                "Min 4 trading days — grind strategies naturally satisfy this; avoid one-shot lottery days.",
                "After a −$250–400 day, cut exposure rather than revenge-trading into the $1,250 wall.",
            ],
            "payout_ops": [
                "Every green day: withdraw 100% of that day's profit — do not rebuild cushion in-account.",
                "Only locked withdrawals count as real money; unpaid open PnL under this mode is ~same-day only.",
                f"After a red day, size off the new lower day-start; the ${RULES.daily_loss_dollars:,.0f} DLL stays fixed in dollars.",
                "Skipping a green-day withdraw reintroduces unpaid-tower risk — don't.",
                "Track locked dollars withdrawn; that is the real scoreboard under this ops mode.",
            ],
            "improvement_levers": [
                "Cut sleeve vol so worst day PnL stays well inside −$1,250.",
                "Prefer books whose daily-withdraw path never touches the $20k floor.",
                "Raise vol slowly only while rolling fail rate stays <10% AND funded breach stays near 0.",
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
    print(
        "Best paycheck:",
        best_paycheck["name"],
        f"locked={best_paycheck['full_2y']['funded_payout']['avg_locked_trader']:.1%}",
        f"fundBreach={best_paycheck['full_2y']['funded_payout']['breach_rate']:.1%}",
        f"hoardLost={best_paycheck['full_2y']['funded_hoard']['avg_unpaid_lost']:.1%}",
    )
    return payload


if __name__ == "__main__":
    run()
