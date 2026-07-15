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
    find_first_full_pass_start,
    random_start_challenges,
    rolling_challenges,
    rolling_funded,
    summarize_attempts,
    summarize_funded,
    simulate_challenge,
    walk_challenge_to_funded,
    walk_daily_withdraw,
)
from src.ftmo_strategies import (
    COMMOD,
    CRYPTO,
    FTMO_TICKERS,
    FX,
    FX_EXTRA,
    INDICES,
    RATES_INTL,
    SECTORS,
    STOCK_CFD,
    STOCK_EXTRA,
    STRATEGY_BUILDERS,
    STRATEGY_META,
    TOP10_V1_IDS,
    VERSION_META,
)
from src.metrics import summarize

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "ftmo_lab.json"

# Emphasize recent regime; still score full ~2Y path for attempt counts
START = "2023-07-01"
RULES = FtmoRules()
ATTEMPT_STEP = 5
# Living policy: withdraw closed excess only when equity ≥ $25k.
PAYOUT = PayoutPolicy(
    every_n_days=1,
    min_profit=0.0,
    keep_buffer=0.0,
    trader_split=0.80,
    max_days=252,
    mode="above_initial",
)
FUNDED_STEP = 10
# Monte Carlo random-start challenge stress (reproducible).
MC_DRAWS = 200
MC_SEED = 42
MC_MIN_REMAINING = 100


def activity_stats(rets: pd.Series) -> dict:
    """How often the book is actually in the market (vs flat / micro)."""
    r = rets.fillna(0.0)
    n = max(len(r), 1)
    abs_r = r.abs()
    active = abs_r > 1e-8
    # ~21 trading days / month → trade-day rate → trades_per_month proxy
    months = n / 21.0
    trades_per_month = float(active.sum() / months) if months > 0 else 0.0
    return {
        "active_day_rate": round(float(active.mean()), 4),
        "flat_day_rate": round(float((abs_r < 1e-10).mean()), 4),
        "micro_day_rate": round(float((abs_r < 0.0005).mean()), 4),
        "mean_abs_return": round(float(abs_r.mean()), 6),
        "turnover_proxy": round(float(r.diff().abs().mean()), 6),
        "n_active_days": int(active.sum()),
        "n_days": int(n),
        "trades_per_month": round(trades_per_month, 2),
        "meets_20tpm": bool(trades_per_month >= 20.0 - 1e-9),
    }


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


def _journey_pack(rets: pd.Series, *, sid: str, name: str) -> dict:
    """
    Continuous P1 (+10%) → reset → P2 (+5%) → reset → funded profit path.
    Prefers the first start that clears both challenge phases when available.
    """
    r = rets.fillna(0.0)
    start_idx = find_first_full_pass_start(r, step=ATTEMPT_STEP, rules=RULES, min_remaining=80)
    j = walk_challenge_to_funded(r, start_idx, RULES, max_funded_days=PAYOUT.max_days)
    return {
        "id": sid,
        "name": name,
        "status": j.status,
        "start": j.start,
        "start_idx": int(start_idx),
        "phase1_days": j.phase1_days,
        "phase2_days": j.phase2_days,
        "funded_days": j.funded_days,
        "locked_profit": round(float(j.locked_profit), 6),
        "locked_profit_dollars": round(dollars(j.locked_profit, RULES), 2),
        "locked_trader_dollars": round(dollars(j.locked_profit * PAYOUT.trader_split, RULES), 2),
        "end_equity": round(float(j.end_equity), 6),
        "end_equity_dollars": round(dollars(j.end_equity, RULES), 2),
        "fail_reason": j.fail_reason,
        "markers": j.markers,
        "points": j.points,
        "phase1_target": RULES.phase1_target,
        "phase2_target": RULES.phase2_target,
        "phase1_target_dollars": round(dollars(1.0 + RULES.phase1_target, RULES), 2),
        "phase2_target_dollars": round(dollars(1.0 + RULES.phase2_target, RULES), 2),
    }


def _slice_rets(rets: pd.Series, end: pd.Timestamp, calendar_days: int | None) -> pd.Series:
    if calendar_days is None:
        return rets
    start = end - pd.Timedelta(days=calendar_days)
    return rets.loc[(rets.index >= start) & (rets.index <= end)]


def score_strategy(
    chal: dict,
    metrics: dict,
    recent: dict,
    funded: dict,
    hoard: dict,
    mc: dict | None = None,
) -> dict:
    """
    Composite for FTMO goals (fail-first + random-start robustness + pace):
      1) Never fail Phase 1/2 under random start dates (Monte Carlo)
      2) Still pass challenge — and clear P1/P2 in fewer trading days
      3) Lock consistent payouts (breach must not eat the stack)
      4) Room to improve = safe but not maxed return
    """
    fail_rate = float(chal["fail_rate"]) if "fail_rate" in chal else 1.0
    pass_rate = float(chal["full_pass_rate"]) if "full_pass_rate" in chal else 0.0
    p1_rate = float(chal["phase1_pass_rate"]) if "phase1_pass_rate" in chal else 0.0
    room = chal.get("avg_room_on_pass")
    room_score = float(room) if room is not None else 0.0
    avg_days = chal.get("avg_days_to_full_pass")
    med_days = chal.get("median_days_to_full_pass")

    mc = mc or {}
    mc_fail = float(mc.get("fail_rate") if mc.get("fail_rate") is not None else fail_rate)
    mc_p1_fail = float(mc.get("phase1_fail_rate") or 0.0)
    mc_p2_fail = float(mc.get("phase2_fail_rate") or 0.0)
    mc_pass = float(mc.get("full_pass_rate") if mc.get("full_pass_rate") is not None else pass_rate)
    mc_zero = bool(mc.get("zero_fail_p1_p2", mc_fail <= 1e-12))
    mc_n = int(mc.get("n_attempts") or 0)

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

    # Pace: ~45 trading days to full pass → ~1.0; 90 → 0.5; 180 → 0.25
    if avg_days is not None and pass_rate >= 0.05:
        pace_score = 1.0 / (1.0 + float(avg_days) / 45.0)
        if med_days is not None:
            pace_score = 0.65 * pace_score + 0.35 * (1.0 / (1.0 + float(med_days) / 45.0))
    else:
        pace_score = 0.0

    # Random-start robustness — primary "don't fail P1/P2" gate
    mc_survival = (
        0.45 * (1.0 - mc_fail)
        + 0.20 * (1.0 - mc_p1_fail)
        + 0.15 * (1.0 - mc_p2_fail)
        + 0.20 * mc_pass
    )

    survival = (
        0.22 * (1.0 - fail_rate)
        + 0.10 * (1.0 - fund_breach)
        + 0.10 * pass_rate
        + 0.06 * p1_rate
        + 0.08 * (1.0 - r_fail)
        + 0.04 * r_pass
        + 0.04 * min(max(room_score, 0.0), 0.15) / 0.15
        + 0.03 * min(max(sharpe, -1.0), 2.5) / 2.5
        + 0.05 * min(pay_hit, 1.0)
        + 0.28 * mc_survival
    )

    ret_util = min(max(cagr, 0.0), 0.25) / 0.25
    safety_gate = max(0.0, 1.0 - max(fail_rate, mc_fail) / 0.20)
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
        0.40 * survival
        + 0.18 * payout_score
        + 0.14 * return_score
        + 0.07 * improvement_room
        + 0.16 * pace_score
        + 0.05 * (1.0 if mc_zero else 0.0)
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
    # Hard preference: any random-start P1/P2 breach is costly
    if mc_n >= 30 and mc_fail > 0:
        composite -= 0.10 + min(mc_fail, 0.35) * 0.25
    if mc_n >= 30 and mc_p1_fail > 0:
        composite -= 0.06
    if mc_n >= 30 and mc_p2_fail > 0:
        composite -= 0.05
    if avg_days is not None and pass_rate >= 0.15 and float(avg_days) > 150:
        composite -= 0.04
    if avg_days is not None and pass_rate >= 0.15 and float(avg_days) > 200:
        composite -= 0.04

    return {
        "survival_score": round(float(survival), 4),
        "return_score": round(float(return_score), 4),
        "improvement_room": round(float(improvement_room), 4),
        "payout_score": round(float(payout_score), 4),
        "pace_score": round(float(pace_score), 4),
        "mc_survival_score": round(float(mc_survival), 4),
        "avg_days_to_full_pass": None if avg_days is None else round(float(avg_days), 1),
        "composite": round(float(composite), 4),
        "recent_pass_avg": round(float(r_pass), 4),
        "recent_fail_avg": round(float(r_fail), 4),
        "recent_sharpe_avg": round(float(r_sharpe), 4),
        "continuous_dd_ok": continuous_ok,
        "avg_locked_trader": round(locked, 4),
        "avg_unpaid_lost": round(lost, 4),
        "fund_breach_rate": round(fund_breach, 4),
        "payout_edge_vs_hoard": round(float(payout_edge), 4),
        "mc_zero_fail_p1_p2": mc_zero,
        "mc_fail_rate": round(mc_fail, 4),
        "mc_phase1_fail_rate": round(mc_p1_fail, 4),
        "mc_phase2_fail_rate": round(mc_p2_fail, 4),
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
        mc_attempts = random_start_challenges(
            rets,
            n_draws=MC_DRAWS,
            seed=MC_SEED,
            rules=RULES,
            min_remaining=MC_MIN_REMAINING,
        )
        mc = summarize_attempts(mc_attempts)
        scores = score_strategy(full["chal"], full["metrics"], recent, funded, hoard, mc)
        activity = activity_stats(rets)

        headroom = full["chal"].get("avg_room_on_pass")
        fail_n = full["chal"]["fails"]
        row = {
            "id": sid,
            "name": meta.name,
            "family": meta.family,
            "thesis": meta.thesis,
            "markets": meta.markets,
            "scores": scores,
            "activity": activity,
            "full_2y": {
                "metrics": full["metrics"],
                "challenge": full["chal"],
                "random_start_mc": mc,
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
            f"MC fail P1={mc['phase1_fail_rate']:.1%} P2={mc['phase2_fail_rate']:.1%} "
            f"zeroFail={'Y' if mc['zero_fail_p1_p2'] else 'N'} "
            f"fundBreach={funded['breach_rate']:.1%} locked={funded['avg_locked_trader']:.1%} "
            f"Sharpe={full['metrics']['sharpe']:.2f} "
            f"active={activity['active_day_rate']:.0%} composite={scores['composite']:.3f}"
        )

    rows.sort(key=lambda r: r["scores"]["composite"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i

    winner = rows[0]
    safe = [
        r
        for r in rows
        if r["full_2y"]["challenge"]["fail_rate"] <= 0.05
        and r["full_2y"].get("random_start_mc", {}).get("zero_fail_p1_p2", False)
    ]
    least_fail = min(
        rows,
        key=lambda r: (
            r["full_2y"].get("random_start_mc", {}).get("fail_rate", 1.0),
            r["full_2y"]["challenge"]["fail_rate"],
            -r["full_2y"]["challenge"]["full_pass_rate"],
            -r["scores"]["composite"],
        ),
    )
    zero_fail_mc = [
        r for r in rows if r["full_2y"].get("random_start_mc", {}).get("zero_fail_p1_p2")
    ]
    best_zero_fail = max(
        zero_fail_mc or rows,
        key=lambda r: (
            r["scores"]["composite"],
            r["full_2y"].get("random_start_mc", {}).get("full_pass_rate", 0.0),
            -r["full_2y"].get("random_start_mc", {}).get("fail_rate", 1.0),
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
    fastest_pool = [
        r
        for r in rows
        if r["full_2y"]["challenge"]["full_pass_rate"] >= 0.20
        and r["full_2y"]["challenge"].get("avg_days_to_full_pass") is not None
        and r["full_2y"]["challenge"]["fail_rate"] <= 0.25
    ] or [
        r
        for r in rows
        if r["full_2y"]["challenge"].get("avg_days_to_full_pass") is not None
    ]
    fastest_challenge = min(
        fastest_pool,
        key=lambda r: (
            r["full_2y"]["challenge"]["avg_days_to_full_pass"],
            r["full_2y"]["challenge"]["fail_rate"],
            -r["scores"]["composite"],
        ),
    )
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
    most_active = max(rows, key=lambda r: r.get("activity", {}).get("active_day_rate", 0.0))
    most_trades = max(rows, key=lambda r: r.get("activity", {}).get("trades_per_month", 0.0))
    tpm_ok = sum(1 for r in rows if r.get("activity", {}).get("meets_20tpm"))
    by_id = {r["id"]: r for r in rows}
    pd_active = by_id.get("pass_defend_active")
    pd_base = by_id.get("pass_defend")
    rp_active = by_id.get("rp_dual_blend_active")
    rp_base = by_id.get("rp_dual_blend")

    def sibling_pack(base, active, *, base_id: str, active_id: str, note: str) -> dict:
        return {
            "base_id": base_id,
            "active_id": active_id,
            "base_name": (base or {}).get("name"),
            "active_name": (active or {}).get("name"),
            "base_active_day_rate": (base or {}).get("activity", {}).get("active_day_rate"),
            "active_active_day_rate": (active or {}).get("activity", {}).get("active_day_rate"),
            "base_flat_day_rate": (base or {}).get("activity", {}).get("flat_day_rate"),
            "active_flat_day_rate": (active or {}).get("activity", {}).get("flat_day_rate"),
            "base_composite": (base or {}).get("scores", {}).get("composite"),
            "active_composite": (active or {}).get("scores", {}).get("composite"),
            "base_rank": (base or {}).get("rank"),
            "active_rank": (active or {}).get("rank"),
            "note": note,
        }

    # Winner recent window curves for UI
    winner_rets = STRATEGY_BUILDERS[winner["id"]](prices).reindex(prices.index).fillna(0.0)
    focus_curves = {
        "2Y": _curve(winner_rets, step=3, daily_loss=RULES.daily_loss),
        "6M": _curve(_slice_rets(winner_rets, end, 183), step=1, daily_loss=RULES.daily_loss),
        "3M": _curve(_slice_rets(winner_rets, end, 92), step=1, daily_loss=RULES.daily_loss),
        "1M": _curve(_slice_rets(winner_rets, end, 31), step=1, daily_loss=RULES.daily_loss),
    }
    risk_visuals = build_risk_visuals(winner_rets, rows, RULES)

    # Challenge → funded journeys (P1 +10% → reset → P2 +5% → reset → funded profits)
    journey_ids = []
    for sid in (
        winner["id"],
        "pass_defend",
        "pass_defend_active",
        "rp_dual_blend",
        "rp_dual_blend_active",
    ):
        if sid in STRATEGY_BUILDERS and sid not in journey_ids:
            journey_ids.append(sid)
    journeys = {}
    print("Building challenge→funded journeys…")
    for sid in journey_ids:
        jrets = STRATEGY_BUILDERS[sid](prices).reindex(prices.index).fillna(0.0)
        pack = _journey_pack(jrets, sid=sid, name=STRATEGY_META[sid].name)
        journeys[sid] = pack
        print(
            f"  journey {sid}: status={pack['status']} "
            f"P1={pack['phase1_days']}d P2={pack['phase2_days']}d "
            f"funded={pack['funded_days']}d locked=${pack['locked_profit_dollars']:,.0f}"
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            f"Research model: ${RULES.initial_balance:,.0f} account, fixed "
            f"${RULES.daily_loss_dollars:,.0f} daily loss, "
            f"${RULES.max_loss_dollars:,.0f} max loss from start "
            f"(floor ${RULES.max_loss_floor_dollars:,.0f}). "
            "Withdraw closed excess only when equity ≥ $25k (nothing while underwater; no open/floating PnL). "
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
                "Withdrawals use closed EOD equity only — no open / floating position PnL.",
                "Nothing is withdrawable while equity < $25k; only excess above $25k is locked, then equity resets to $25k.",
                "Challenge phases still require equity growth (no mid-phase withdraw) so pass rates stay measurable.",
                "Kill × markers use the funded closed-withdraw path.",
                "Fail tallies count daily-loss and max-loss breaches; timeouts are separate.",
            ],
        },
        "universe": {
            "start": str(prices.index[0].date()),
            "end": str(prices.index[-1].date()),
            "n_days": int(len(prices)),
            "tickers": FTMO_TICKERS,
            "n_strategies": len(rows),
            "top10_v1": TOP10_V1_IDS,
            "version_methods": {
                str(k): {"label": v[0], "thesis": v[1]} for k, v in VERSION_META.items()
            },
            "groups": {
                "fx": FX + FX_EXTRA,
                "indices": INDICES,
                "sectors": SECTORS,
                "rates_intl": RATES_INTL,
                "commod": COMMOD,
                "crypto": CRYPTO,
                "stock_cfd": STOCK_CFD + STOCK_EXTRA,
            },
        },
        "ranking_rubric": {
            "survival": "Zero Phase 1/2 fails under random-start Monte Carlo + low rolling fail + funded breach",
            "random_start_mc": f"{MC_DRAWS} random challenge starts (seed={MC_SEED}); gate is no P1/P2 daily/max breaches",
            "pace": "Clear Phase 1 (+10%) and Phase 2 (+5%) in fewer trading days (target ~45–90d full pass)",
            "payout": "Locked trader payouts under closed-above-$25k withdraw; unpaid lost on breach stays small",
            "return": "Sharpe / Sortino / CAGR + locked paycheck yield",
            "improvement_room": "Safe but not maxed — worth carefully leveraging",
            "composite": "0.40 survival (incl. MC) + 0.18 payout + 0.16 pace + 0.14 return + 0.07 improvement + zero-fail bonus",
        },
        "random_start_mc": {
            "n_draws": MC_DRAWS,
            "seed": MC_SEED,
            "min_remaining_days": MC_MIN_REMAINING,
            "note": (
                "Each strategy is launched from 200 randomly sampled start dates. "
                "A Phase 1/2 fail = hit −$1,250 daily or −$5k max on that attempt. "
                "Timeouts (too slow) are tracked separately — zero_fail_p1_p2 means no daily/max breaches."
            ),
            "n_zero_fail_books": len(zero_fail_mc),
            "n_strategies": len(rows),
        },
        "payout_policy": {
            "assumption": "Withdraw closed excess above $25k only. Underwater = $0 withdrawable until back at initial.",
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
                "mc_fail_rate": least_fail["full_2y"].get("random_start_mc", {}).get("fail_rate"),
                "mc_zero_fail_p1_p2": least_fail["full_2y"].get("random_start_mc", {}).get("zero_fail_p1_p2"),
            },
            "zero_fail_random_start": {
                "id": best_zero_fail["id"],
                "name": best_zero_fail["name"],
                "n_zero_fail_books": len(zero_fail_mc),
                "mc_fail_rate": best_zero_fail["full_2y"].get("random_start_mc", {}).get("fail_rate"),
                "mc_phase1_fail_rate": best_zero_fail["full_2y"].get("random_start_mc", {}).get("phase1_fail_rate"),
                "mc_phase2_fail_rate": best_zero_fail["full_2y"].get("random_start_mc", {}).get("phase2_fail_rate"),
                "mc_full_pass_rate": best_zero_fail["full_2y"].get("random_start_mc", {}).get("full_pass_rate"),
                "mc_n_attempts": best_zero_fail["full_2y"].get("random_start_mc", {}).get("n_attempts"),
                "composite": best_zero_fail["scores"]["composite"],
                "note": (
                    f"Best composite among {len(zero_fail_mc)} books with zero Phase 1/2 breaches "
                    f"across {MC_DRAWS} random start dates."
                ),
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
            "fastest_challenge": {
                "id": fastest_challenge["id"],
                "name": fastest_challenge["name"],
                "avg_days_to_full_pass": fastest_challenge["full_2y"]["challenge"].get("avg_days_to_full_pass"),
                "median_days_to_full_pass": fastest_challenge["full_2y"]["challenge"].get("median_days_to_full_pass"),
                "full_pass_rate": fastest_challenge["full_2y"]["challenge"]["full_pass_rate"],
                "fail_rate": fastest_challenge["full_2y"]["challenge"]["fail_rate"],
                "pace_score": fastest_challenge["scores"].get("pace_score"),
                "note": "Fewest avg trading days to clear Phase 1 (+10%) + Phase 2 (+5%) among books with usable pass rate.",
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
            "most_active": {
                "id": most_active["id"],
                "name": most_active["name"],
                "active_day_rate": most_active.get("activity", {}).get("active_day_rate"),
                "flat_day_rate": most_active.get("activity", {}).get("flat_day_rate"),
                "trades_per_month": most_active.get("activity", {}).get("trades_per_month"),
                "composite": most_active["scores"]["composite"],
                "note": "Highest share of non-flat trading days under the $25k closed-withdraw model.",
            },
            "most_trades": {
                "id": most_trades["id"],
                "name": most_trades["name"],
                "trades_per_month": most_trades.get("activity", {}).get("trades_per_month"),
                "meets_20tpm": most_trades.get("activity", {}).get("meets_20tpm"),
                "active_day_rate": most_trades.get("activity", {}).get("active_day_rate"),
                "composite": most_trades["scores"]["composite"],
                "note": "Highest trade-days / month (target ≥20). Active-day proxy on closed daily PnL.",
            },
            "trade_more_board": {
                "n_strategies": len(rows),
                "n_meeting_20tpm": tpm_ok,
                "version_methods": {
                    str(k): {"label": v[0], "thesis": v[1]} for k, v in VERSION_META.items()
                },
                "note": (
                    "Bakeoff = top-10 V1 books + V2–V5 variants (~50). "
                    "V2 faster signals · V3 wide universe · V4 challenge pace (hit +10%/+5% sooner) · "
                    "V5 always-in rebalancer."
                ),
            },
            "active_sibling": sibling_pack(
                pd_base,
                pd_active,
                base_id="pass_defend",
                active_id="pass_defend_active",
                note=(
                    "Pass-then-defend · Active is the higher-frequency sibling of the top book: "
                    "shorter momentum lookbacks, fast TSMOM sleeve, softer brake → far fewer flat days."
                ),
            ),
            "rp_dual_sibling": sibling_pack(
                rp_base,
                rp_active,
                base_id="rp_dual_blend",
                active_id="rp_dual_blend_active",
                note=(
                    "RP + Dual-mom · Active keeps the RP/dual/grind core but adds a fast TSMOM sleeve, "
                    "shorter dual-mom lookback, and softer brake so it trades more often."
                ),
            ),
        },
        "strategies": rows,
        "winner_focus_curves": focus_curves,
        "sibling_focus_curves": {
            "pass_defend": {
                "base_6m": curves.get("pass_defend__6m", []),
                "active_6m": curves.get("pass_defend_active__6m", []),
            },
            "rp_dual": {
                "base_6m": curves.get("rp_dual_blend__6m", []),
                "active_6m": curves.get("rp_dual_blend_active__6m", []),
            },
            # Back-compat aliases used by older page snippets
            "base_6m": curves.get("pass_defend__6m", []),
            "active_6m": curves.get("pass_defend_active__6m", []),
        },
        "challenge_journeys": {
            "default_id": winner["id"] if winner["id"] in journeys else (journey_ids[0] if journey_ids else None),
            "ids": journey_ids,
            "phase1_target": RULES.phase1_target,
            "phase2_target": RULES.phase2_target,
            "note": (
                "Phase 1 needs +10% closed equity (no mid-phase withdraw), then resets to $25k. "
                "Phase 2 needs +5%, then resets again. Funded phase withdraws closed excess ≥ $25k "
                "and tallies locked profit — the live ops scoreboard."
            ),
            "by_id": journeys,
        },
        "risk_visuals": risk_visuals,
        "curves": {r["id"]: curves[r["id"]] for r in rows},
        "curves_6m": {r["id"]: curves[f"{r['id']}__6m"] for r in rows},
        "playbook": {
            "recommended": winner["id"],
            "challenge_ops": [
                f"Hard stop before −${RULES.daily_loss_dollars:,.0f} day PnL on the ${RULES.initial_balance:,.0f} account.",
                f"Never let equity pierce ${RULES.max_loss_floor_dollars:,.0f} (max −${RULES.max_loss_dollars:,.0f} from start).",
                "Challenge phases still need equity in-account to hit +10% / +5% (sim only) — prefer V4 Challenge pace siblings when base books grind too long.",
                "Min 4 trading days — grind strategies naturally satisfy this; avoid one-shot lottery days.",
                "After a −$250–400 day, cut exposure rather than revenge-trading into the $1,250 wall.",
            ],
            "payout_ops": [
                "Only withdraw after positions are closed for the day (EOD equity).",
                "If account < $25k: withdraw $0 — let equity rebuild to initial first.",
                "If account > $25k: pull excess down to $25k and lock that paycheck.",
                f"After a red day, size off the new day-start; the ${RULES.daily_loss_dollars:,.0f} DLL stays fixed in dollars.",
                "Track locked dollars withdrawn; that is the real scoreboard under this ops mode.",
            ],
            "improvement_levers": [
                "Cut sleeve vol so worst day PnL stays well inside −$1,250.",
                "Prefer books whose closed-withdraw path never touches the $20k floor.",
                "Raise vol slowly only while rolling fail rate stays <10% AND funded breach stays near 0.",
                "If the winner sits flat too often, promote a V2–V5 trade-more sibling "
                "(faster signals / wider book / sleeve stack / always-in) that still clears fail-first gates.",
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
        f"MC fail={least_fail['full_2y'].get('random_start_mc', {}).get('fail_rate', 0):.1%}",
    )
    print(
        f"Random-start zero P1/P2 fail: {len(zero_fail_mc)}/{len(rows)} books · "
        f"best={best_zero_fail['name']} MC pass="
        f"{best_zero_fail['full_2y'].get('random_start_mc', {}).get('full_pass_rate', 0):.0%}"
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
        "Fastest challenge:",
        fastest_challenge["name"],
        f"avg_days={fastest_challenge['full_2y']['challenge'].get('avg_days_to_full_pass')}",
        f"fail={fastest_challenge['full_2y']['challenge']['fail_rate']:.1%}",
    )
    print(
        "Best paycheck:",
        best_paycheck["name"],
        f"locked={best_paycheck['full_2y']['funded_payout']['avg_locked_trader']:.1%}",
        f"fundBreach={best_paycheck['full_2y']['funded_payout']['breach_rate']:.1%}",
        f"hoardLost={best_paycheck['full_2y']['funded_hoard']['avg_unpaid_lost']:.1%}",
    )
    print(
        f"Trade-more: {tpm_ok}/{len(rows)} books ≥20 trade-days/mo · "
        f"top TPM={most_trades['name']} @ {most_trades.get('activity', {}).get('trades_per_month')}"
    )
    if pd_active and pd_base:
        print(
            "Pass-defend Active:",
            f"active={pd_active['activity']['active_day_rate']:.0%}",
            f"(base {pd_base['activity']['active_day_rate']:.0%})",
            f"composite={pd_active['scores']['composite']:.3f}",
        )
    if rp_active and rp_base:
        print(
            "RP Dual Active:",
            f"active={rp_active['activity']['active_day_rate']:.0%}",
            f"(base {rp_base['activity']['active_day_rate']:.0%})",
            f"composite={rp_active['scores']['composite']:.3f}",
        )
    return payload


if __name__ == "__main__":
    run()
