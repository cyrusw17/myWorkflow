"""
Prop-account rule simulator (research approximation).

Operating assumption (user):
  Account size:          $25,000
  Daily loss limit:      $1,250 fixed (not a % of current equity)
  Max loss from start:   $5,000  → equity floor $20,000
  Each day: withdraw all day profit so the account never compounds above
            the post-drawdown day-start (cushion does not rebuild from wins)

Challenge-phase targets (kept for bakeoff scoring; equity must grow so
challenge walks do NOT withdraw mid-phase):
  Phase 1: +10% of initial · Phase 2: +5% of initial · min 4 trading days

Daily loss / equity use closed daily PnL as a proxy (no intraday marks).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FtmoRules:
    # Dollar account (canonical display + absolute limits)
    initial_balance: float = 25_000.0
    daily_loss_dollars: float = 1_250.0  # fixed $ from day-start balance
    max_loss_dollars: float = 5_000.0  # static from initial → floor $20k
    # Unit-equity equivalents (initial = 1.0): $1250/$25k = 0.05, $5k/$25k = 0.20
    phase1_target: float = 0.10
    phase2_target: float = 0.05
    daily_loss: float = 1_250.0 / 25_000.0  # fraction of INITIAL, subtracted from day-start
    max_loss: float = 5_000.0 / 25_000.0  # fraction of INITIAL (static floor at 0.80)
    min_trading_days: int = 4
    # FTMO 2-Step has no hard time limit; we still cap so rolling sims finish.
    max_days_phase1: int = 252
    max_days_phase2: int = 180

    @property
    def max_loss_floor(self) -> float:
        return 1.0 - self.max_loss

    @property
    def max_loss_floor_dollars(self) -> float:
        return self.initial_balance - self.max_loss_dollars


def dollars(frac: float, rules: FtmoRules | None = None) -> float:
    """Convert unit-equity fraction to dollars on the modeled account."""
    r = rules or FtmoRules()
    return float(frac) * r.initial_balance


def walk_daily_withdraw(
    rets: pd.Series,
    rules: FtmoRules | None = None,
    *,
    stop_on_breach: bool = True,
) -> tuple[pd.Series, list[dict], float]:
    """
    Equity path with "withdraw all day profit" ops.

    - Loss days stick (account balance falls).
    - Profit days withdraw the day's PnL → equity stays at day_start.
    - Daily kill: post-trade equity < day_start − $1,250 (0.05 of initial).
    - Max kill: post-trade equity < $20,000 (0.80 of initial).

    By default stops at the first breach (account is dead). Returns
    (equity_series, kill_events, locked_profit_frac).
    """
    rules = rules or FtmoRules()
    r = rets.fillna(0.0)
    eq = 1.0
    locked = 0.0
    eqs: list[float] = []
    kills: list[dict] = []
    floor = rules.max_loss_floor
    daily_abs = rules.daily_loss  # fraction of initial
    dead = False

    for dt, ret in r.items():
        if dead:
            eqs.append(eq)
            continue
        day_start = eq
        gross = day_start * (1.0 + float(ret))
        day_pnl = gross - day_start
        daily_kill = gross < day_start - daily_abs - 1e-12
        max_kill = gross < floor - 1e-12
        if daily_kill or max_kill:
            kills.append({
                "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                "equity": round(float(gross), 6),
                "equity_dollars": round(dollars(gross, rules), 2),
                "day_start": round(float(day_start), 6),
                "day_start_dollars": round(dollars(day_start, rules), 2),
                "day_pnl": round(float(day_pnl), 6),
                "day_pnl_dollars": round(dollars(day_pnl, rules), 2),
                "day_return": round(float(ret), 6),
                "reason": "daily" if daily_kill else "max",
                "daily_kill": bool(daily_kill),
                "max_kill": bool(max_kill),
            })
            eq = gross
            eqs.append(eq)
            if stop_on_breach:
                dead = True
            elif day_pnl > 0:
                locked += day_pnl
                eq = day_start
                eqs[-1] = eq
            continue
        if day_pnl > 0:
            locked += day_pnl
            eq = day_start  # withdraw all profit
        else:
            eq = gross
        eqs.append(eq)

    equity = pd.Series(eqs, index=r.index, dtype=float)
    return equity, kills, float(locked)


@dataclass
class PhaseResult:
    status: str  # pass | fail_daily | fail_max | timeout
    days: int
    trading_days: int
    end_equity: float
    min_equity: float
    peak_equity: float
    max_dd_from_start: float
    room_to_floor: float  # equity − 0.90 at end (or last day)
    hit_target_day: int | None


@dataclass
class ChallengeResult:
    status: str  # full_pass | fail_phase1 | fail_phase2 | timeout_phase1 | timeout_phase2
    phase1: PhaseResult
    phase2: PhaseResult | None
    start: str
    fail_reason: str | None


def _run_phase(
    rets: pd.Series,
    target: float,
    rules: FtmoRules,
    max_days: int,
) -> PhaseResult:
    """Walk daily returns from equity=1.0 under FTMO static/daily floors."""
    eq = 1.0
    peak = 1.0
    floor = rules.max_loss_floor
    trading_days = 0
    min_eq = 1.0
    hit_day = None
    status = "timeout"
    last_i = -1
    n = len(rets)

    for i, (dt, r) in enumerate(rets.items()):
        last_i = i
        day_start = eq
        daily_floor = day_start - rules.daily_loss
        if float(r) != 0.0:
            trading_days += 1

        eq *= 1.0 + float(r)
        peak = max(peak, eq)
        min_eq = min(min_eq, eq)

        if eq < daily_floor - 1e-12:
            status = "fail_daily"
            break
        if eq < floor - 1e-12:
            status = "fail_max"
            break
        if eq >= 1.0 + target - 1e-12 and trading_days >= rules.min_trading_days:
            status = "pass"
            hit_day = i + 1
            break
        if i + 1 >= max_days:
            status = "timeout"
            break

    # Ran out of market data before hitting max_days / pass / fail
    if status == "timeout" and last_i + 1 < min(max_days, n if n < max_days else max_days) and last_i + 1 >= n:
        status = "censored"
    if status == "timeout" and n < max_days and last_i + 1 >= n:
        status = "censored"

    days = last_i + 1 if last_i >= 0 else 0
    room = eq - floor
    return PhaseResult(
        status=status,
        days=days,
        trading_days=trading_days,
        end_equity=float(eq),
        min_equity=float(min_eq),
        peak_equity=float(peak),
        max_dd_from_start=float(min_eq - 1.0),
        room_to_floor=float(room),
        hit_target_day=hit_day,
    )


def simulate_challenge(
    rets: pd.Series,
    start_idx: int,
    rules: FtmoRules | None = None,
) -> ChallengeResult:
    """
    Simulate an independent 2-step attempt starting at start_idx.
    Phase 2 resets to a fresh 1.0 equity book (new Verification account).
    """
    rules = rules or FtmoRules()
    start_ts = rets.index[start_idx]
    p1_slice = rets.iloc[start_idx:]
    phase1 = _run_phase(p1_slice, rules.phase1_target, rules, rules.max_days_phase1)

    if phase1.status == "fail_daily":
        return ChallengeResult("fail_phase1", phase1, None, str(start_ts.date()), "daily_loss")
    if phase1.status == "fail_max":
        return ChallengeResult("fail_phase1", phase1, None, str(start_ts.date()), "max_loss")
    if phase1.status == "censored":
        return ChallengeResult("censored", phase1, None, str(start_ts.date()), "censored")
    if phase1.status != "pass":
        return ChallengeResult("timeout_phase1", phase1, None, str(start_ts.date()), "timeout")

    p2_start = start_idx + phase1.days
    p2_slice = rets.iloc[p2_start:]
    if p2_slice.empty:
        empty = PhaseResult("censored", 0, 0, 1.0, 1.0, 1.0, 0.0, 0.10, None)
        return ChallengeResult("censored", phase1, empty, str(start_ts.date()), "censored")

    phase2 = _run_phase(p2_slice, rules.phase2_target, rules, rules.max_days_phase2)
    if phase2.status == "fail_daily":
        return ChallengeResult("fail_phase2", phase1, phase2, str(start_ts.date()), "daily_loss")
    if phase2.status == "fail_max":
        return ChallengeResult("fail_phase2", phase1, phase2, str(start_ts.date()), "max_loss")
    if phase2.status == "censored":
        return ChallengeResult("censored", phase1, phase2, str(start_ts.date()), "censored")
    if phase2.status != "pass":
        return ChallengeResult("timeout_phase2", phase1, phase2, str(start_ts.date()), "timeout")
    return ChallengeResult("full_pass", phase1, phase2, str(start_ts.date()), None)


def rolling_challenges(
    rets: pd.Series,
    *,
    step: int = 5,
    rules: FtmoRules | None = None,
    min_remaining: int = 60,
) -> list[ChallengeResult]:
    """Launch challenge attempts every `step` trading days across the series."""
    rules = rules or FtmoRules()
    out: list[ChallengeResult] = []
    n = len(rets)
    for i in range(0, max(0, n - min_remaining), step):
        out.append(simulate_challenge(rets, i, rules))
    return out


def summarize_attempts(attempts: list[ChallengeResult]) -> dict:
    # Drop data-censored attempts so short windows don't fake timeouts
    scored = [a for a in attempts if a.status != "censored"]
    censored_n = len(attempts) - len(scored)
    if not scored:
        return {
            "n_attempts": 0,
            "n_launched": len(attempts),
            "n_censored": censored_n,
            "full_pass_rate": 0.0,
            "phase1_pass_rate": 0.0,
            "fail_rate": 0.0,
            "fail_daily": 0,
            "fail_max": 0,
            "timeouts": 0,
            "full_passes": 0,
            "fails": 0,
            "avg_days_to_full_pass": None,
            "avg_room_on_pass": None,
            "avg_min_equity_phase1": None,
            "median_days_to_full_pass": None,
        }

    n = len(scored)
    full = [a for a in scored if a.status == "full_pass"]
    p1_ok = [a for a in scored if a.phase1.status == "pass"]
    fails = [a for a in scored if a.status.startswith("fail_")]
    timeouts = [a for a in scored if a.status.startswith("timeout_")]
    fail_daily = sum(1 for a in scored if a.fail_reason == "daily_loss")
    fail_max = sum(1 for a in scored if a.fail_reason == "max_loss")

    days_full = []
    rooms = []
    for a in full:
        d = a.phase1.days + (a.phase2.days if a.phase2 else 0)
        days_full.append(d)
        rooms.append(a.phase1.room_to_floor)
        if a.phase2:
            rooms.append(a.phase2.room_to_floor)

    min_eqs = [a.phase1.min_equity for a in scored]

    return {
        "n_attempts": n,
        "n_launched": len(attempts),
        "n_censored": censored_n,
        "full_pass_rate": len(full) / n,
        "phase1_pass_rate": len(p1_ok) / n,
        "fail_rate": len(fails) / n,
        "fail_daily": fail_daily,
        "fail_max": fail_max,
        "timeouts": len(timeouts),
        "full_passes": len(full),
        "fails": len(fails),
        "avg_days_to_full_pass": float(np.mean(days_full)) if days_full else None,
        "avg_room_on_pass": float(np.mean(rooms)) if rooms else None,
        "avg_min_equity_phase1": float(np.mean(min_eqs)) if min_eqs else None,
        "median_days_to_full_pass": float(np.median(days_full)) if days_full else None,
    }


def window_mask(index: pd.DatetimeIndex, end: pd.Timestamp, days: int) -> pd.Series:
    start = end - pd.Timedelta(days=days)
    return (index >= start) & (index <= end)


@dataclass(frozen=True)
class PayoutPolicy:
    """
    Funded-account pay-yourself-out policy.

    Default ops (user): withdraw ALL day profit every closed day so equity never
    compounds above the post-drawdown day-start. Locked payouts survive a breach;
    unpaid open profit (usually just same-day PnL under this mode) does not.
    """

    every_n_days: int = 1  # 1 = every trading day
    min_profit: float = 0.0  # any day profit is withdrawn
    keep_buffer: float = 0.0
    trader_split: float = 0.80
    max_days: int = 252
    # day_pnl: pull that day's gain back to day_start (default).
    # above_initial: older cadence pull of equity − (1 + keep_buffer).
    mode: str = "day_pnl"


@dataclass
class FundedPathResult:
    status: str  # survived | fail_daily | fail_max | censored
    days: int
    locked_gross: float  # withdrawn before any breach (fraction of initial)
    locked_trader: float  # after split
    unpaid_lost: float  # open profit lost on breach (0 if survive/flat)
    n_payouts: int
    payout_sizes: list[float]
    min_equity: float
    end_equity: float
    start: str


def simulate_funded_payouts(
    rets: pd.Series,
    start_idx: int = 0,
    rules: FtmoRules | None = None,
    policy: PayoutPolicy | None = None,
) -> FundedPathResult:
    """
    Walk a funded account with regular withdrawals.

    Default (day_pnl): apply return → check $1,250 daily / $5k max → if the day
    is profitable, withdraw day PnL so equity returns to day_start (cushion never
    rebuilds from wins after a drawdown).
    """
    rules = rules or FtmoRules()
    policy = policy or PayoutPolicy()
    path = rets.iloc[start_idx : start_idx + policy.max_days]
    start_ts = rets.index[start_idx]

    if path.empty:
        return FundedPathResult(
            "censored", 0, 0.0, 0.0, 0.0, 0, [], 1.0, 1.0, str(pd.Timestamp(start_ts).date())
        )

    eq = 1.0
    floor = rules.max_loss_floor
    locked = 0.0
    payouts: list[float] = []
    min_eq = 1.0
    peak_since_pay = 1.0
    status = "survived"
    days_since_payout = 0
    last_i = -1
    n = len(path)
    breach_day_pnl = 0.0

    for i, (dt, r) in enumerate(path.items()):
        last_i = i
        day_start = eq
        daily_floor = day_start - rules.daily_loss
        eq = day_start * (1.0 + float(r))
        day_pnl = eq - day_start
        min_eq = min(min_eq, eq)
        peak_since_pay = max(peak_since_pay, eq)
        days_since_payout += 1

        if eq < daily_floor - 1e-12:
            status = "fail_daily"
            breach_day_pnl = max(day_pnl, 0.0)
            break
        if eq < floor - 1e-12:
            status = "fail_max"
            breach_day_pnl = max(day_pnl, 0.0)
            break

        if policy.mode == "day_pnl":
            if days_since_payout >= policy.every_n_days and day_pnl > policy.min_profit + 1e-12:
                locked += day_pnl
                payouts.append(float(day_pnl))
                eq = day_start
                peak_since_pay = eq
                days_since_payout = 0
        elif days_since_payout >= policy.every_n_days:
            open_profit = eq - 1.0
            withdrawable = eq - (1.0 + policy.keep_buffer)
            if open_profit >= policy.min_profit and withdrawable > 1e-12:
                locked += withdrawable
                payouts.append(float(withdrawable))
                eq = 1.0 + policy.keep_buffer
                peak_since_pay = eq
                days_since_payout = 0

    unpaid_lost = 0.0
    if status.startswith("fail_"):
        if policy.mode == "day_pnl":
            unpaid_lost = float(breach_day_pnl)  # usually 0 on a loss-day kill
        else:
            unpaid_lost = max(peak_since_pay - 1.0, 0.0)
    else:
        if policy.mode != "day_pnl":
            withdrawable = eq - (1.0 + policy.keep_buffer)
            if withdrawable > 1e-12 and (eq - 1.0) >= policy.min_profit * 0.5:
                locked += withdrawable
                payouts.append(float(withdrawable))
                eq = 1.0 + policy.keep_buffer
        if last_i + 1 >= n and n < min(40, policy.max_days):
            status = "censored"

    days = last_i + 1 if last_i >= 0 else 0
    return FundedPathResult(
        status=status,
        days=days,
        locked_gross=float(locked),
        locked_trader=float(locked * policy.trader_split),
        unpaid_lost=float(unpaid_lost),
        n_payouts=len(payouts),
        payout_sizes=payouts,
        min_equity=float(min_eq),
        end_equity=float(eq),
        start=str(pd.Timestamp(start_ts).date()),
    )


def simulate_funded_hoard(
    rets: pd.Series,
    start_idx: int = 0,
    rules: FtmoRules | None = None,
    max_days: int = 252,
    trader_split: float = 0.80,
) -> FundedPathResult:
    """Contrast: never withdraw until end — breach loses all open profit."""
    rules = rules or FtmoRules()
    path = rets.iloc[start_idx : start_idx + max_days]
    start_ts = rets.index[start_idx]
    if path.empty:
        return FundedPathResult(
            "censored", 0, 0.0, 0.0, 0.0, 0, [], 1.0, 1.0, str(pd.Timestamp(start_ts).date())
        )

    eq = 1.0
    floor = rules.max_loss_floor
    min_eq = 1.0
    peak = 1.0
    status = "survived"
    last_i = -1
    n = len(path)

    for i, (dt, r) in enumerate(path.items()):
        last_i = i
        day_start = eq
        eq *= 1.0 + float(r)
        min_eq = min(min_eq, eq)
        peak = max(peak, eq)
        if eq < day_start - rules.daily_loss - 1e-12:
            status = "fail_daily"
            break
        if eq < floor - 1e-12:
            status = "fail_max"
            break

    locked = 0.0
    unpaid_lost = 0.0
    payouts: list[float] = []
    if status.startswith("fail_"):
        # Entire unpaid tower above initial is gone
        unpaid_lost = max(peak - 1.0, 0.0)
    else:
        if last_i + 1 >= n and n < max_days:
            status = "censored" if last_i + 1 < 20 else "survived"
        locked = max(eq - 1.0, 0.0)
        if locked > 0:
            payouts = [locked]
            eq = 1.0

    days = last_i + 1 if last_i >= 0 else 0
    return FundedPathResult(
        status=status,
        days=days,
        locked_gross=float(locked),
        locked_trader=float(locked * trader_split),
        unpaid_lost=float(unpaid_lost),
        n_payouts=len(payouts),
        payout_sizes=payouts,
        min_equity=float(min_eq),
        end_equity=float(eq),
        start=str(pd.Timestamp(start_ts).date()),
    )


def rolling_funded(
    rets: pd.Series,
    *,
    step: int = 10,
    rules: FtmoRules | None = None,
    policy: PayoutPolicy | None = None,
    min_remaining: int = 40,
    mode: str = "payout",  # payout | hoard
) -> list[FundedPathResult]:
    rules = rules or FtmoRules()
    policy = policy or PayoutPolicy()
    out: list[FundedPathResult] = []
    n = len(rets)
    for i in range(0, max(0, n - min_remaining), step):
        if mode == "hoard":
            out.append(simulate_funded_hoard(rets, i, rules, policy.max_days, policy.trader_split))
        else:
            out.append(simulate_funded_payouts(rets, i, rules, policy))
    return out


def summarize_funded(paths: list[FundedPathResult]) -> dict:
    scored = [p for p in paths if p.status != "censored"]
    censored_n = len(paths) - len(scored)
    if not scored:
        return {
            "n_paths": 0,
            "n_launched": len(paths),
            "n_censored": censored_n,
            "breach_rate": 0.0,
            "breaches": 0,
            "survived": 0,
            "avg_locked_gross": 0.0,
            "avg_locked_trader": 0.0,
            "avg_unpaid_lost": 0.0,
            "avg_n_payouts": 0.0,
            "payout_hit_rate": 0.0,
            "median_locked_trader": 0.0,
            "payout_cv": None,
            "net_kept_vs_lost": 0.0,
        }

    breaches = [p for p in scored if p.status.startswith("fail_")]
    survived = [p for p in scored if p.status == "survived"]
    locked_t = [p.locked_trader for p in scored]
    locked_g = [p.locked_gross for p in scored]
    lost = [p.unpaid_lost for p in scored]
    n_pay = [p.n_payouts for p in scored]
    # Flatten payout sizes for CV (consistency of paycheck stream)
    all_pays = [x for p in scored for x in p.payout_sizes]
    if len(all_pays) >= 2 and float(np.mean(all_pays)) > 1e-12:
        payout_cv = float(np.std(all_pays) / np.mean(all_pays))
    else:
        payout_cv = None

    avg_locked_t = float(np.mean(locked_t))
    avg_lost = float(np.mean(lost))
    return {
        "n_paths": len(scored),
        "n_launched": len(paths),
        "n_censored": censored_n,
        "breach_rate": len(breaches) / len(scored),
        "breaches": len(breaches),
        "survived": len(survived),
        "avg_locked_gross": float(np.mean(locked_g)),
        "avg_locked_trader": avg_locked_t,
        "avg_unpaid_lost": avg_lost,
        "avg_n_payouts": float(np.mean(n_pay)),
        "payout_hit_rate": float(np.mean([1.0 if p.n_payouts > 0 else 0.0 for p in scored])),
        "median_locked_trader": float(np.median(locked_t)),
        "payout_cv": payout_cv,
        "net_kept_vs_lost": avg_locked_t - avg_lost * 0.80,  # compare trader-split apples
    }
