"""
Prop-account rule simulator (research approximation).

Operating assumption (user):
  Account size:          $25,000
  Daily loss limit:      $1,250 fixed (not a % of current equity)
  Max loss from start:   $5,000  → equity floor $20,000
  Withdrawals:
    - Only from closed EOD equity (no open / floating PnL)
    - Only when account value is ≥ $25,000; pull excess down to $25k
    - If underwater (< $25k), nothing is withdrawn — cushion rebuilds first

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
) -> tuple[pd.Series, list[dict], float, pd.Series]:
    """
    Equity path with closed-position withdrawals only when ≥ initial.

    - Apply closed daily return → check $1,250 daily / $5k max on that EOD equity.
    - If closed equity > $25k: withdraw (equity − $25k), reset account to $25k.
    - If closed equity ≤ $25k: no withdrawal (cannot take profit while underwater).
    - Open / floating PnL is never withdrawn — only closed EOD marks.

    By default stops at the first breach (account is dead). Returns
    (equity_series, kill_events, locked_profit_frac, cumulative_locked_series).
    """
    rules = rules or FtmoRules()
    r = rets.fillna(0.0)
    eq = 1.0
    locked = 0.0
    eqs: list[float] = []
    locked_path: list[float] = []
    kills: list[dict] = []
    floor = rules.max_loss_floor
    daily_abs = rules.daily_loss  # fraction of initial
    dead = False

    for dt, ret in r.items():
        if dead:
            eqs.append(eq)
            locked_path.append(locked)
            continue
        day_start = eq
        # Closed EOD equity only (daily return proxy — no open-position marks).
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
                "locked_profit": round(float(locked), 6),
                "locked_profit_dollars": round(dollars(locked, rules), 2),
                "reason": "daily" if daily_kill else "max",
                "daily_kill": bool(daily_kill),
                "max_kill": bool(max_kill),
            })
            eq = gross
            eqs.append(eq)
            locked_path.append(locked)
            if stop_on_breach:
                dead = True
            continue

        # Withdraw closed profit only while account ≥ $25k (initial = 1.0).
        if gross > 1.0 + 1e-12:
            withdraw = gross - 1.0
            locked += withdraw
            eq = 1.0
        else:
            # Underwater or flat: nothing withdrawable; cushion rebuilds toward $25k.
            eq = gross
        eqs.append(eq)
        locked_path.append(locked)

    equity = pd.Series(eqs, index=r.index, dtype=float)
    locked_s = pd.Series(locked_path, index=r.index, dtype=float)
    return equity, kills, float(locked), locked_s


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


def random_start_challenges(
    rets: pd.Series,
    *,
    n_draws: int = 200,
    seed: int = 42,
    rules: FtmoRules | None = None,
    min_remaining: int = 100,
) -> list[ChallengeResult]:
    """
    Monte Carlo challenge stress: launch independent 2-step attempts from
    randomly sampled start dates (reproducible via `seed`).

    Used to verify Phase 1 / Phase 2 do not breach $1,250 daily or $5k max
    across many launch dates — not just a fixed rolling grid.
    """
    rules = rules or FtmoRules()
    r = rets.fillna(0.0)
    n = len(r)
    hi = max(0, n - min_remaining)
    if hi <= 0 or n_draws <= 0:
        return []
    rng = np.random.default_rng(int(seed))
    replace = hi < n_draws
    idxs = rng.choice(hi, size=int(n_draws), replace=replace)
    # Sort for stable logs; each attempt is independent of order.
    return [simulate_challenge(r, int(i), rules) for i in sorted(int(x) for x in idxs)]


@dataclass
class ChallengeJourney:
    """
    Continuous P1 → reset → P2 → reset → funded path for graphing.

    Challenge phases keep equity in-account (no mid-phase withdraw).
    On each phase pass the book resets to 1.0. Funded phase locks closed
    excess above initial under walk_daily_withdraw rules.
    """

    status: str  # full_funded | fail_phase1 | fail_phase2 | timeout_phase1 | timeout_phase2 | fail_funded | censored
    start: str
    points: list[dict]
    markers: list[dict]
    phase1_days: int
    phase2_days: int
    funded_days: int
    locked_profit: float
    end_equity: float
    fail_reason: str | None


def walk_challenge_to_funded(
    rets: pd.Series,
    start_idx: int = 0,
    rules: FtmoRules | None = None,
    *,
    max_funded_days: int = 252,
) -> ChallengeJourney:
    """
    Walk one continuous journey: Phase 1 (+10%) → reset → Phase 2 (+5%) →
    reset → funded (closed excess ≥ $25k withdrawable).

    Points are EOD marks with phase labels for Charts.js. Equity drops to 1.0
    at each phase reset; locked_profit only grows after funded starts.
    """
    rules = rules or FtmoRules()
    r = rets.fillna(0.0)
    if start_idx >= len(r):
        return ChallengeJourney(
            "censored",
            "",
            [],
            [],
            0,
            0,
            0,
            0.0,
            1.0,
            "censored",
        )

    start_ts = r.index[start_idx]
    floor = rules.max_loss_floor
    daily_abs = rules.daily_loss
    points: list[dict] = []
    markers: list[dict] = [
        {
            "day": 0,
            "date": pd.Timestamp(start_ts).strftime("%Y-%m-%d"),
            "event": "start",
            "label": "Challenge start · Phase 1 (+10%)",
            "equity": 1.0,
        }
    ]

    def _append(
        *,
        dt,
        eq: float,
        phase: str,
        locked: float,
        day_i: int,
        event: str | None = None,
        kill: bool = False,
        day_start: float | None = None,
        day_pnl: float | None = None,
    ) -> None:
        points.append(
            {
                "day": day_i,
                "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                "phase": phase,
                "equity": round(float(eq), 6),
                "equity_dollars": round(dollars(eq, rules), 2),
                "profit_tally": round(float(locked), 6),
                "profit_tally_dollars": round(dollars(locked, rules), 2),
                "total_dollars": round(dollars(eq, rules) + dollars(locked, rules), 2),
                "target": round(
                    1.0 + (rules.phase1_target if phase == "phase1" else rules.phase2_target if phase == "phase2" else 0.0),
                    6,
                )
                if phase in ("phase1", "phase2")
                else None,
                "target_dollars": round(
                    dollars(
                        1.0
                        + (
                            rules.phase1_target
                            if phase == "phase1"
                            else rules.phase2_target
                            if phase == "phase2"
                            else 0.0
                        ),
                        rules,
                    ),
                    2,
                )
                if phase in ("phase1", "phase2")
                else None,
                "kill": bool(kill),
                "event": event,
                "day_start": round(float(day_start), 6) if day_start is not None else None,
                "day_pnl": round(float(day_pnl), 6) if day_pnl is not None else None,
            }
        )

    def _run_challenge_phase(
        slice_rets: pd.Series,
        *,
        phase: str,
        target: float,
        max_days: int,
        day_offset: int,
    ) -> tuple[str, int, float, str | None]:
        """Returns (status, days_consumed, end_equity, fail_reason)."""
        eq = 1.0
        trading_days = 0
        last_i = -1
        n = len(slice_rets)
        for i, (dt, ret) in enumerate(slice_rets.items()):
            last_i = i
            day_start = eq
            if float(ret) != 0.0:
                trading_days += 1
            gross = day_start * (1.0 + float(ret))
            day_pnl = gross - day_start
            daily_kill = gross < day_start - daily_abs - 1e-12
            max_kill = gross < floor - 1e-12
            eq = gross
            day_i = day_offset + i + 1
            if daily_kill or max_kill:
                _append(
                    dt=dt,
                    eq=eq,
                    phase=phase,
                    locked=0.0,
                    day_i=day_i,
                    event="kill",
                    kill=True,
                    day_start=day_start,
                    day_pnl=day_pnl,
                )
                reason = "daily_loss" if daily_kill else "max_loss"
                return f"fail_{phase}", i + 1, eq, reason
            hit = eq >= 1.0 + target - 1e-12 and trading_days >= rules.min_trading_days
            _append(
                dt=dt,
                eq=eq,
                phase=phase,
                locked=0.0,
                day_i=day_i,
                event="phase_pass" if hit else None,
                day_start=day_start,
                day_pnl=day_pnl,
            )
            if hit:
                return "pass", i + 1, eq, None
            if i + 1 >= max_days:
                return "timeout", i + 1, eq, "timeout"
        days = last_i + 1 if last_i >= 0 else 0
        if days < max_days and days >= n:
            return "censored", days, eq, "censored"
        return "timeout", days, eq, "timeout"

    # ——— Phase 1 ———
    p1_slice = r.iloc[start_idx:]
    p1_status, p1_days, p1_eq, p1_fail = _run_challenge_phase(
        p1_slice,
        phase="phase1",
        target=rules.phase1_target,
        max_days=rules.max_days_phase1,
        day_offset=0,
    )
    if p1_status != "pass":
        status = {
            "fail_phase1": "fail_phase1",
            "timeout": "timeout_phase1",
            "censored": "censored",
        }.get(p1_status, "fail_phase1")
        return ChallengeJourney(
            status,
            str(pd.Timestamp(start_ts).date()),
            points,
            markers,
            p1_days,
            0,
            0,
            0.0,
            float(p1_eq),
            p1_fail,
        )

    markers.append(
        {
            "day": p1_days,
            "date": points[-1]["date"],
            "event": "pass_phase1",
            "label": f"Phase 1 passed (+{rules.phase1_target:.0%}) · reset → Phase 2",
            "equity": round(float(p1_eq), 6),
        }
    )
    # Visible reset tick before Phase 2 begins (same calendar day end / next start)
    markers.append(
        {
            "day": p1_days,
            "date": points[-1]["date"],
            "event": "reset_phase2",
            "label": "Reset to $25k · Phase 2 (+5%)",
            "equity": 1.0,
        }
    )

    # ——— Phase 2 ———
    p2_start = start_idx + p1_days
    p2_slice = r.iloc[p2_start:]
    if p2_slice.empty:
        return ChallengeJourney(
            "censored",
            str(pd.Timestamp(start_ts).date()),
            points,
            markers,
            p1_days,
            0,
            0,
            0.0,
            1.0,
            "censored",
        )

    p2_status, p2_days, p2_eq, p2_fail = _run_challenge_phase(
        p2_slice,
        phase="phase2",
        target=rules.phase2_target,
        max_days=rules.max_days_phase2,
        day_offset=p1_days,
    )
    if p2_status != "pass":
        status = {
            "fail_phase2": "fail_phase2",
            "timeout": "timeout_phase2",
            "censored": "censored",
        }.get(p2_status, "fail_phase2")
        return ChallengeJourney(
            status,
            str(pd.Timestamp(start_ts).date()),
            points,
            markers,
            p1_days,
            p2_days,
            0,
            0.0,
            float(p2_eq),
            p2_fail,
        )

    markers.append(
        {
            "day": p1_days + p2_days,
            "date": points[-1]["date"],
            "event": "pass_phase2",
            "label": f"Phase 2 passed (+{rules.phase2_target:.0%}) · reset → Funded",
            "equity": round(float(p2_eq), 6),
        }
    )
    markers.append(
        {
            "day": p1_days + p2_days,
            "date": points[-1]["date"],
            "event": "funded_start",
            "label": "Official funded · withdraw closed excess ≥ $25k",
            "equity": 1.0,
        }
    )

    # ——— Funded (closed-above-initial withdraw) ———
    funded_start = p2_start + p2_days
    funded_slice = r.iloc[funded_start : funded_start + max_funded_days]
    eq = 1.0
    locked = 0.0
    funded_days = 0
    status = "full_funded"
    fail_reason = None

    if funded_slice.empty:
        return ChallengeJourney(
            "censored",
            str(pd.Timestamp(start_ts).date()),
            points,
            markers,
            p1_days,
            p2_days,
            0,
            0.0,
            1.0,
            "censored",
        )

    for i, (dt, ret) in enumerate(funded_slice.items()):
        day_start = eq
        gross = day_start * (1.0 + float(ret))
        day_pnl = gross - day_start
        daily_kill = gross < day_start - daily_abs - 1e-12
        max_kill = gross < floor - 1e-12
        day_i = p1_days + p2_days + i + 1
        funded_days = i + 1

        if daily_kill or max_kill:
            _append(
                dt=dt,
                eq=gross,
                phase="funded",
                locked=locked,
                day_i=day_i,
                event="kill",
                kill=True,
                day_start=day_start,
                day_pnl=day_pnl,
            )
            status = "fail_funded"
            fail_reason = "daily_loss" if daily_kill else "max_loss"
            markers.append(
                {
                    "day": day_i,
                    "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                    "event": "kill",
                    "label": f"Funded kill · {fail_reason}",
                    "equity": round(float(gross), 6),
                }
            )
            return ChallengeJourney(
                status,
                str(pd.Timestamp(start_ts).date()),
                points,
                markers,
                p1_days,
                p2_days,
                funded_days,
                float(locked),
                float(gross),
                fail_reason,
            )

        if gross > 1.0 + 1e-12:
            withdraw = gross - 1.0
            locked += withdraw
            eq = 1.0
            event = "withdraw"
        else:
            eq = gross
            event = None

        _append(
            dt=dt,
            eq=eq,
            phase="funded",
            locked=locked,
            day_i=day_i,
            event=event,
            day_start=day_start,
            day_pnl=day_pnl,
        )

    return ChallengeJourney(
        status,
        str(pd.Timestamp(start_ts).date()),
        points,
        markers,
        p1_days,
        p2_days,
        funded_days,
        float(locked),
        float(eq),
        fail_reason,
    )


def find_first_full_pass_start(
    rets: pd.Series,
    *,
    step: int = 5,
    rules: FtmoRules | None = None,
    min_remaining: int = 80,
) -> int:
    """Start index of the *fastest* full P1+P2 clear (falls back to 0)."""
    rules = rules or FtmoRules()
    n = len(rets)
    best_i = 0
    best_days = None
    for i in range(0, max(0, n - min_remaining), step):
        shot = simulate_challenge(rets, i, rules)
        if shot.status != "full_pass":
            continue
        days = shot.phase1.days + (shot.phase2.days if shot.phase2 else 0)
        if best_days is None or days < best_days:
            best_days = days
            best_i = i
            # Early exit if we already have a very fast pass (~6 weeks)
            if days <= 30:
                break
    return best_i


def summarize_attempts(attempts: list[ChallengeResult]) -> dict:
    # Drop data-censored attempts so short windows don't fake timeouts
    scored = [a for a in attempts if a.status != "censored"]
    censored_n = len(attempts) - len(scored)
    empty = {
        "n_attempts": 0,
        "n_launched": len(attempts),
        "n_censored": censored_n,
        "full_pass_rate": 0.0,
        "phase1_pass_rate": 0.0,
        "phase1_fail_rate": 0.0,
        "phase2_fail_rate": 0.0,
        "phase2_fail_given_p1": 0.0,
        "fail_rate": 0.0,
        "fail_daily": 0,
        "fail_max": 0,
        "fail_phase1": 0,
        "fail_phase2": 0,
        "timeouts": 0,
        "full_passes": 0,
        "fails": 0,
        "avg_days_to_full_pass": None,
        "avg_room_on_pass": None,
        "avg_min_equity_phase1": None,
        "median_days_to_full_pass": None,
        "zero_fail_p1_p2": True,
        "p05_days_to_full_pass": None,
        "p95_days_to_full_pass": None,
    }
    if not scored:
        return empty

    n = len(scored)
    full = [a for a in scored if a.status == "full_pass"]
    p1_ok = [a for a in scored if a.phase1.status == "pass"]
    fails = [a for a in scored if a.status.startswith("fail_")]
    timeouts = [a for a in scored if a.status.startswith("timeout_")]
    fail_p1 = [a for a in scored if a.status == "fail_phase1"]
    fail_p2 = [a for a in scored if a.status == "fail_phase2"]
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
    reached_p2 = len(p1_ok)

    return {
        "n_attempts": n,
        "n_launched": len(attempts),
        "n_censored": censored_n,
        "full_pass_rate": len(full) / n,
        "phase1_pass_rate": len(p1_ok) / n,
        "phase1_fail_rate": len(fail_p1) / n,
        "phase2_fail_rate": len(fail_p2) / n,
        "phase2_fail_given_p1": (len(fail_p2) / reached_p2) if reached_p2 else 0.0,
        "fail_rate": len(fails) / n,
        "fail_daily": fail_daily,
        "fail_max": fail_max,
        "fail_phase1": len(fail_p1),
        "fail_phase2": len(fail_p2),
        "timeouts": len(timeouts),
        "full_passes": len(full),
        "fails": len(fails),
        "avg_days_to_full_pass": float(np.mean(days_full)) if days_full else None,
        "avg_room_on_pass": float(np.mean(rooms)) if rooms else None,
        "avg_min_equity_phase1": float(np.mean(min_eqs)) if min_eqs else None,
        "median_days_to_full_pass": float(np.median(days_full)) if days_full else None,
        "zero_fail_p1_p2": len(fails) == 0,
        "p05_days_to_full_pass": float(np.percentile(days_full, 5)) if days_full else None,
        "p95_days_to_full_pass": float(np.percentile(days_full, 95)) if days_full else None,
    }


def window_mask(index: pd.DatetimeIndex, end: pd.Timestamp, days: int) -> pd.Series:
    start = end - pd.Timedelta(days=days)
    return (index >= start) & (index <= end)


@dataclass(frozen=True)
class PayoutPolicy:
    """
    Funded-account pay-yourself-out policy.

    Default ops (user): after each closed day, if equity ≥ $25k initial,
    withdraw excess down to $25k. Nothing withdrawable while underwater.
    Only closed EOD equity counts — no open-position / floating PnL pulls.
    """

    every_n_days: int = 1  # 1 = every closed trading day
    min_profit: float = 0.0  # any excess above initial is withdrawable
    keep_buffer: float = 0.0  # leave account exactly at initial after payout
    trader_split: float = 0.80
    max_days: int = 252
    # above_initial: pull equity − (1 + keep_buffer) when ≥ initial (default).
    # day_pnl: legacy — pull day gain even while underwater.
    mode: str = "above_initial"


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

    Default (above_initial): apply closed return → check $1,250 daily / $5k max →
    if closed equity > $25k, withdraw excess back to $25k. While underwater,
    no withdrawal — cushion rebuilds toward initial before profit is lockable.
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
    breach_open_above_initial = 0.0

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
            breach_open_above_initial = max(eq - 1.0, 0.0)
            break
        if eq < floor - 1e-12:
            status = "fail_max"
            breach_open_above_initial = max(eq - 1.0, 0.0)
            break

        if policy.mode == "day_pnl":
            # Legacy: withdraw day gain even underwater (not current user ops).
            if days_since_payout >= policy.every_n_days and day_pnl > policy.min_profit + 1e-12:
                locked += day_pnl
                payouts.append(float(day_pnl))
                eq = day_start
                peak_since_pay = eq
                days_since_payout = 0
        elif days_since_payout >= policy.every_n_days:
            # Closed positions only; withdraw only when ≥ $25k initial.
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
            unpaid_lost = 0.0
        else:
            unpaid_lost = float(breach_open_above_initial)
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
