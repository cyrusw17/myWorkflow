"""
Topstep Trading Combine® + Express Funded Account (XFA) rule approximations.

Modeled product (from Topstep UI / public rules — verify before trading):
  150K Buying Power · Combine fee $199 · Reset $199 · XFA activation $149

Trading Combine (150K):
  Profit target:          $9,000
  Maximum Loss Limit:     $4,500 (trailing vs end-of-day high-water; Combine often
                          trails more tightly — we use EOD HWM − $4,500)
  Max position:           15 contracts (soft daily PnL cap as proxy)
  Consistency:            best single day ≤ 50% of cumulative Combine profit
                          (else keep trading until ratio clears)

Express Funded Account (XFA) — Official Topstep rules (Jun 2025+):
  Start balance:          $0 with MLL = −$4,500 on 150K
  MLL:                    based on highest EOD balance; does not drop when you lose
  After MLL trails to $0: account locks at $0 floor
  Hitting/going through MLL: account permanently closed

  Standard payout path:
    - 5 Winning Days of $150+ net
    - Withdraw up to 50% of reward balance, capped at $5,000
    - Trader keeps 90% (Topstep 10%)

  Consistency XFA path:
    - Min 3 trading days + 40% consistency target
      (largest winning day ≤ 40% of total net profit in the payout window)
    - Withdraw up to 50% of reward balance, capped at $6,000
    - Trader keeps 90%

Research proxy: multi-asset daily returns are scaled to dollar PnL on the
$150k buying-power notional. Not live TopstepX fills, fees, or contract margins.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Topstep150k:
    buying_power: float = 150_000.0
    combine_fee: float = 199.0
    reset_fee: float = 199.0
    xfa_activation: float = 149.0
    profit_target: float = 9_000.0
    max_loss_limit: float = 4_500.0  # absolute $ distance from HWM / start
    max_contracts: int = 15
    # Soft daily |pnl| ceiling (~15 contracts × ES $50/pt × ~10 pts)
    max_day_pnl: float = 7_500.0
    combine_consistency: float = 0.50  # best day / total profit
    winning_day_dollars: float = 150.0
    trader_split: float = 0.90
    # Standard XFA
    standard_win_days: int = 5
    standard_payout_cap: float = 5_000.0
    # Consistency XFA
    consistency_min_days: int = 3
    consistency_target: float = 0.40  # best day / total ≤ 40%
    consistency_payout_cap: float = 6_000.0
    payout_fraction: float = 0.50  # up to 50% of reward balance
    max_combine_days: int = 120
    max_xfa_days: int = 252


def returns_to_dollars(rets: pd.Series, rules: Topstep150k | None = None) -> pd.Series:
    """Map unit strategy returns → dollar day PnL on 150K buying-power notional."""
    rules = rules or Topstep150k()
    r = rets.fillna(0.0).astype(float)
    raw = r * rules.buying_power
    return raw.clip(-rules.max_day_pnl, rules.max_day_pnl)


@dataclass
class CombineResult:
    status: str  # pass | fail_mll | timeout | censored
    days: int
    end_balance: float
    min_balance: float
    peak_balance: float
    best_day: float
    consistency_ratio: float | None
    winning_days: int
    start: str
    curve: list[dict] = field(default_factory=list)


@dataclass
class XfaResult:
    status: str  # survived | fail_mll | censored
    path: str  # standard | consistency
    days: int
    end_balance: float
    min_balance: float
    n_payouts: int
    locked_trader: float  # dollars kept after 90/10
    locked_gross: float
    winning_days: int
    start: str
    curve: list[dict] = field(default_factory=list)
    payouts: list[dict] = field(default_factory=list)


def simulate_combine(
    day_pnl: pd.Series,
    start_idx: int = 0,
    rules: Topstep150k | None = None,
) -> CombineResult:
    """
    Walk a Trading Combine from start_idx.
    Pass when balance ≥ $9k and best_day / balance ≤ 50%.
    Fail when balance ≤ trailing MLL (HWM − $4,500).
    """
    rules = rules or Topstep150k()
    path = day_pnl.iloc[start_idx : start_idx + rules.max_combine_days].fillna(0.0)
    if path.empty:
        return CombineResult("censored", 0, 0.0, 0.0, 0.0, 0.0, None, 0, "")

    start_ts = path.index[0]
    bal = 0.0
    hwm = 0.0
    mll = -rules.max_loss_limit
    min_bal = 0.0
    best_day = 0.0
    win_days = 0
    curve: list[dict] = []
    status = "timeout"
    last_i = -1

    for i, (dt, pnl) in enumerate(path.items()):
        last_i = i
        pnl = float(pnl)
        bal += pnl
        min_bal = min(min_bal, bal)
        if pnl >= rules.winning_day_dollars:
            win_days += 1
        if pnl > best_day:
            best_day = pnl

        # EOD trailing MLL vs peak closed balance
        if bal > hwm:
            hwm = bal
            mll = hwm - rules.max_loss_limit

        cons = (best_day / bal) if bal > 1e-9 else None
        curve.append(
            {
                "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                "balance": round(bal, 2),
                "day_pnl": round(pnl, 2),
                "mll": round(mll, 2),
                "hwm": round(hwm, 2),
                "consistency": None if cons is None else round(float(cons), 4),
            }
        )

        if bal <= mll + 1e-9:
            status = "fail_mll"
            break

        if bal >= rules.profit_target - 1e-9:
            # Consistency gate: best day ≤ 50% of total profit
            if cons is not None and cons <= rules.combine_consistency + 1e-12:
                status = "pass"
                break
            # else keep grinding until other days dilute best-day share

    days = last_i + 1 if last_i >= 0 else 0
    if status == "timeout" and days < min(40, rules.max_combine_days) and days >= len(path):
        status = "censored"

    end_cons = (best_day / bal) if bal > 1e-9 else None
    return CombineResult(
        status=status,
        days=days,
        end_balance=float(bal),
        min_balance=float(min_bal),
        peak_balance=float(hwm),
        best_day=float(best_day),
        consistency_ratio=None if end_cons is None else float(end_cons),
        winning_days=win_days,
        start=str(pd.Timestamp(start_ts).date()),
        curve=curve,
    )


def _consistency_ok(day_pnls: list[float], target: float) -> bool:
    """Best winning day ≤ target share of total net profit in the payout window."""
    total = sum(day_pnls)
    if total <= 1e-9:
        return False
    wins = [x for x in day_pnls if x > 0]
    if not wins:
        return False
    best = max(wins)
    return (best / total) <= target + 1e-12


def simulate_xfa(
    day_pnl: pd.Series,
    start_idx: int = 0,
    rules: Topstep150k | None = None,
    *,
    path: str = "standard",  # standard | consistency
) -> XfaResult:
    """
    Express Funded walk with EOD-trailing MLL and chosen payout path.
    After each payout, Topstep locks MLL at $0 (account cannot go negative).
    """
    rules = rules or Topstep150k()
    assert path in ("standard", "consistency")
    series = day_pnl.iloc[start_idx : start_idx + rules.max_xfa_days].fillna(0.0)
    if series.empty:
        return XfaResult("censored", path, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, "")

    start_ts = series.index[0]
    bal = 0.0
    hwm = 0.0
    mll = -rules.max_loss_limit
    mll_locked_zero = False
    min_bal = 0.0
    win_days_since_pay = 0
    trade_days_since_pay = 0
    window_pnls: list[float] = []
    locked_trader = 0.0
    locked_gross = 0.0
    payouts: list[dict] = []
    curve: list[dict] = []
    status = "survived"
    last_i = -1

    payout_cap = (
        rules.standard_payout_cap if path == "standard" else rules.consistency_payout_cap
    )

    for i, (dt, pnl) in enumerate(series.items()):
        last_i = i
        pnl = float(pnl)
        bal += pnl
        min_bal = min(min_bal, bal)
        trade_days_since_pay += 1
        window_pnls.append(pnl)
        if pnl >= rules.winning_day_dollars:
            win_days_since_pay += 1

        if not mll_locked_zero:
            if bal > hwm:
                hwm = bal
                mll = hwm - rules.max_loss_limit
            # Once HWM − MLL distance collapses to start, MLL locks at 0
            if mll >= -1e-9:
                mll = 0.0
                mll_locked_zero = True
        else:
            mll = 0.0

        killed = bal <= mll + 1e-9
        curve.append(
            {
                "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                "balance": round(bal, 2),
                "day_pnl": round(pnl, 2),
                "mll": round(mll, 2),
                "locked_trader": round(locked_trader, 2),
                "win_days_cycle": win_days_since_pay,
            }
        )

        if killed:
            status = "fail_mll"
            break

        # Payout eligibility
        eligible = False
        if path == "standard":
            eligible = win_days_since_pay >= rules.standard_win_days and bal > 125.0
        else:
            eligible = (
                trade_days_since_pay >= rules.consistency_min_days
                and bal > 125.0
                and _consistency_ok(window_pnls, rules.consistency_target)
            )

        if eligible and bal > 0:
            gross = min(bal * rules.payout_fraction, payout_cap)
            if gross >= 125.0:
                trader = gross * rules.trader_split
                locked_gross += gross
                locked_trader += trader
                bal -= gross
                # Official: after payout MLL resets / locks at $0
                mll = 0.0
                mll_locked_zero = True
                hwm = max(hwm, bal)
                payouts.append(
                    {
                        "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                        "gross": round(gross, 2),
                        "trader": round(trader, 2),
                        "balance_after": round(bal, 2),
                    }
                )
                win_days_since_pay = 0
                trade_days_since_pay = 0
                window_pnls = []

    days = last_i + 1 if last_i >= 0 else 0
    if status == "survived" and days < 40 and days >= len(series):
        status = "censored"

    return XfaResult(
        status=status,
        path=path,
        days=days,
        end_balance=float(bal),
        min_balance=float(min_bal),
        n_payouts=len(payouts),
        locked_trader=float(locked_trader),
        locked_gross=float(locked_gross),
        winning_days=sum(1 for x in series if float(x) >= rules.winning_day_dollars),
        start=str(pd.Timestamp(start_ts).date()),
        curve=curve,
        payouts=payouts,
    )


def random_combine_starts(
    day_pnl: pd.Series,
    *,
    n_draws: int = 150,
    seed: int = 42,
    rules: Topstep150k | None = None,
    min_remaining: int = 60,
) -> list[CombineResult]:
    rules = rules or Topstep150k()
    n = len(day_pnl)
    hi = max(0, n - min_remaining)
    if hi <= 0:
        return []
    rng = np.random.default_rng(seed)
    idxs = rng.choice(hi, size=min(n_draws, max(hi, 1)), replace=(hi < n_draws))
    return [simulate_combine(day_pnl, int(i), rules) for i in idxs]


def summarize_combines(results: list[CombineResult]) -> dict:
    scored = [r for r in results if r.status != "censored"]
    if not scored:
        return {
            "n": 0,
            "pass_rate": 0.0,
            "fail_mll_rate": 0.0,
            "timeout_rate": 0.0,
            "avg_days_to_pass": None,
            "median_days_to_pass": None,
            "avg_end_on_pass": None,
        }
    n = len(scored)
    passes = [r for r in scored if r.status == "pass"]
    fails = [r for r in scored if r.status == "fail_mll"]
    timeouts = [r for r in scored if r.status == "timeout"]
    days = [r.days for r in passes]
    return {
        "n": n,
        "pass_rate": len(passes) / n,
        "fail_mll_rate": len(fails) / n,
        "timeout_rate": len(timeouts) / n,
        "passes": len(passes),
        "fails_mll": len(fails),
        "timeouts": len(timeouts),
        "avg_days_to_pass": float(np.mean(days)) if days else None,
        "median_days_to_pass": float(np.median(days)) if days else None,
        "avg_end_on_pass": float(np.mean([r.end_balance for r in passes])) if passes else None,
        "zero_fail_mll": len(fails) == 0,
    }
