"""
Topstep 150K lab — screen top steady books, then one winner through Combine → XFA.

No challenge-pace / Phase-1 speedups (no pass_defend, challenge_sprint, V4).
Winner is used as the SINGLE book across Combine + Express Funded.

Outputs site/data/topstep_lab.json for site/topstep-lab.html.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data import load_universe
from src.ftmo_strategies import FTMO_TICKERS, TOP10_V1_IDS, V1_BUILDERS, V1_META
from src.metrics import summarize
from src.topstep_rules import (
    Topstep150k,
    random_combine_starts,
    returns_to_dollars,
    simulate_combine,
    simulate_xfa,
    summarize_combines,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "topstep_lab.json"

START = "2023-07-01"
RULES = Topstep150k()
MC_DRAWS = 150
MC_SEED = 42
SCREEN_DRAWS = 80

# Phase-1 "speedup" books — excluded from Topstep screening
EXCLUDE_IDS = {
    "pass_defend",
    "pass_defend_active",
    "challenge_sprint",
}

# Extra steady V1 books worth trying under Topstep rules
EXTRA_CANDIDATES = [
    "risk_parity_vt10",
    "risk_parity_vt7",
    "rp_dual_blend",
    "rp_dual_blend_active",
    "index_grind_vt10",
    "index_grind_vt6",
    "dual_mom_vt8",
    "ftmo_grind",
    "gold_fx_vt6",
    "tsmom_multi_vt8",
]


def _candidate_ids() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for sid in list(TOP10_V1_IDS) + EXTRA_CANDIDATES:
        if sid in EXCLUDE_IDS or sid in seen or sid not in V1_BUILDERS:
            continue
        seen.add(sid)
        out.append(sid)
    return out


def _downsample_curve(curve: list[dict], step: int = 2) -> list[dict]:
    if len(curve) <= 80 or step <= 1:
        return curve
    keep = set(range(0, len(curve), step))
    keep.add(len(curve) - 1)
    return [curve[i] for i in sorted(keep)]


def _rank_key(row: dict) -> tuple:
    """Top-performing: maximize pass − fail, then faster pass times."""
    pass_r = float(row.get("pass_rate") or 0.0)
    fail = float(row.get("fail_mll_rate") or 1.0)
    score = pass_r - fail
    days = float(row.get("avg_days_to_pass") or 999.0)
    return (-score, days, -pass_r)


def main() -> dict:
    cands = _candidate_ids()
    print(f"Loading universe for Topstep lab · screening {len(cands)} steady books…")
    prices = load_universe(FTMO_TICKERS, start=START)
    end = prices.index[-1]
    two_y = end - pd.Timedelta(days=365 * 2 + 14)
    prices = prices.loc[prices.index >= two_y]
    print(
        f"Prices: {prices.shape[0]} days × {prices.shape[1]}  "
        f"({prices.index[0].date()} → {prices.index[-1].date()})"
    )

    screen_rows: list[dict] = []
    dollar_cache: dict[str, pd.Series] = {}

    for sid in cands:
        print(f"  screen {sid}…")
        rets = V1_BUILDERS[sid](prices).reindex(prices.index).fillna(0.0)
        dollars = returns_to_dollars(rets, RULES)
        dollar_cache[sid] = dollars
        mc = summarize_combines(
            random_combine_starts(
                dollars, n_draws=SCREEN_DRAWS, seed=MC_SEED, rules=RULES
            )
        )
        meta = V1_META.get(sid)
        screen_rows.append(
            {
                "id": sid,
                "name": meta.name if meta else sid,
                "family": meta.family if meta else "",
                "pass_rate": mc["pass_rate"],
                "fail_mll_rate": mc["fail_mll_rate"],
                "timeout_rate": mc["timeout_rate"],
                "avg_days_to_pass": mc.get("avg_days_to_pass"),
                "median_days_to_pass": mc.get("median_days_to_pass"),
                "zero_fail_mll": mc.get("zero_fail_mll", False),
                "n": mc["n"],
            }
        )

    screen_rows.sort(key=_rank_key)
    winner_id = screen_rows[0]["id"] if screen_rows else "risk_parity_vt10"
    print(
        f"Winner: {winner_id} "
        f"(pass={screen_rows[0]['pass_rate']:.1%} fail={screen_rows[0]['fail_mll_rate']:.1%})"
    )

    meta = V1_META[winner_id]
    rets = V1_BUILDERS[winner_id](prices).reindex(prices.index).fillna(0.0)
    dollars = dollar_cache[winner_id] if winner_id in dollar_cache else returns_to_dollars(rets, RULES)
    metrics = summarize(rets, winner_id)

    combine = simulate_combine(dollars, 0, RULES)
    # If calendar start fails/times out, show a representative Random-pass Combine for charts
    if combine.status != "pass":
        for att in random_combine_starts(
            dollars, n_draws=MC_DRAWS, seed=MC_SEED, rules=RULES
        ):
            if att.status == "pass":
                combine = att
                print(
                    f"Calendar start missed — using pass path @ {combine.start} "
                    f"({combine.days}d bal=${combine.end_balance:,.0f})"
                )
                break
    print(f"Combine display: {combine.status} days={combine.days} bal=${combine.end_balance:,.0f}")

    # Express starts the day after Combine pass when possible
    if combine.status == "pass" and combine.curve:
        end_date = pd.Timestamp(combine.curve[-1]["date"])
        try:
            xfa_start = int(dollars.index.get_loc(end_date)) + 1
        except KeyError:
            xfa_start = combine.days
    else:
        xfa_start = 0
    if xfa_start >= len(dollars) - 20:
        xfa_start = max(0, len(dollars) // 3)
    xfa_std = simulate_xfa(dollars, xfa_start, RULES, path="standard")
    xfa_con = simulate_xfa(dollars, xfa_start, RULES, path="consistency")
    print(
        f"XFA Standard: {xfa_std.status} payouts={xfa_std.n_payouts} "
        f"locked_trader=${xfa_std.locked_trader:,.0f}"
    )
    print(
        f"XFA Consistency: {xfa_con.status} payouts={xfa_con.n_payouts} "
        f"locked_trader=${xfa_con.locked_trader:,.0f}"
    )

    print(f"Random-start Combine MC ({MC_DRAWS} draws) on winner…")
    mc = summarize_combines(
        random_combine_starts(dollars, n_draws=MC_DRAWS, seed=MC_SEED, rules=RULES)
    )
    print(
        f"  pass={mc['pass_rate']:.1%} fail_mll={mc['fail_mll_rate']:.1%} "
        f"timeout={mc['timeout_rate']:.1%} avg_days={mc.get('avg_days_to_pass')}"
    )

    mc_attempts = random_combine_starts(
        dollars, n_draws=MC_DRAWS, seed=MC_SEED, rules=RULES
    )
    xfa_from_passes = []
    for att in mc_attempts:
        if att.status != "pass" or not att.curve:
            continue
        end_date = pd.Timestamp(att.curve[-1]["date"])
        try:
            idx = dollars.index.get_loc(end_date)
        except KeyError:
            continue
        nxt = int(idx) + 1
        if nxt >= len(dollars) - 40:
            continue
        xfa_from_passes.append(simulate_xfa(dollars, nxt, RULES, path="standard"))
        if len(xfa_from_passes) >= 40:
            break

    if xfa_from_passes:
        xfa_breach = sum(1 for x in xfa_from_passes if x.status == "fail_mll") / len(
            xfa_from_passes
        )
        xfa_avg_locked = float(
            sum(x.locked_trader for x in xfa_from_passes) / len(xfa_from_passes)
        )
        xfa_pay_hit = float(
            sum(1 for x in xfa_from_passes if x.n_payouts > 0) / len(xfa_from_passes)
        )
    else:
        xfa_breach = xfa_avg_locked = xfa_pay_hit = 0.0

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Research approximation of Topstep 150K Trading Combine® + Express Funded rules. "
            "Daily multi-asset return proxies ≠ TopstepX futures fills, fees, or scaling plan. "
            "Verify live rules at topstep.com before purchasing."
        ),
        "brand": {
            "name": "Topstep",
            "product": "150K Buying Power · Trading Combine → Express Funded",
            "colors": {
                "bg": "#0a0a0a",
                "blue": "#2f6bff",
                "white": "#ffffff",
                "muted": "#9aa3b2",
            },
        },
        "strategy": {
            "id": winner_id,
            "name": meta.name,
            "family": meta.family,
            "thesis": meta.thesis,
            "note": (
                "Single book for Combine and Express — screened from top steady V1 books. "
                "No challenge-pace / pass-defend / Phase-1 speedups."
            ),
        },
        "screen": {
            "n_candidates": len(screen_rows),
            "excluded": sorted(EXCLUDE_IDS),
            "screen_draws": SCREEN_DRAWS,
            "seed": MC_SEED,
                "note": (
                "Ranked by (pass_rate − fail_mll_rate), then avg days to pass. "
                "Winner used as the only Topstep book."
            ),
            "rows": screen_rows,
        },
        "account": {
            "buying_power": RULES.buying_power,
            "combine_fee": RULES.combine_fee,
            "reset_fee": RULES.reset_fee,
            "xfa_activation": RULES.xfa_activation,
            "profit_target": RULES.profit_target,
            "max_loss_limit": RULES.max_loss_limit,
            "max_contracts": RULES.max_contracts,
            "max_day_pnl_at_full_size": RULES.max_day_pnl,
            "combine_consistency": RULES.combine_consistency,
            "winning_day_dollars": RULES.winning_day_dollars,
            "trader_split": RULES.trader_split,
            "position_rules": {
                "combine": f"Hard cap {RULES.max_contracts} mini contracts (150 micros).",
                "xfa_scaling_150k": [
                    {"balance_lt": 1500, "contracts": 3},
                    {"balance_lt": 2000, "contracts": 4},
                    {"balance_lt": 3000, "contracts": 5},
                    {"balance_lt": 4500, "contracts": 10},
                    {"balance_lt": None, "contracts": 15},
                ],
                "note": "XFA Scaling Plan uses prior EOD balance; size updates next session.",
            },
            "standard": {
                "win_days": RULES.standard_win_days,
                "payout_cap": RULES.standard_payout_cap,
                "payout_fraction": RULES.payout_fraction,
            },
            "consistency_xfa": {
                "min_days": RULES.consistency_min_days,
                "consistency_target": RULES.consistency_target,
                "payout_cap": RULES.consistency_payout_cap,
                "payout_fraction": RULES.payout_fraction,
            },
        },
        "rules_notes": [
            f"${RULES.buying_power:,.0f} buying power · profit target ${RULES.profit_target:,.0f} · MLL ${RULES.max_loss_limit:,.0f}.",
            f"Max position: Combine hard-capped at {RULES.max_contracts} mini contracts (PnL clipped to full-size day ceiling).",
            "XFA Scaling Plan (150K): 3 → 4 → 5 → 10 → 15 contracts by prior EOD balance tiers ($0 / $1.5k / $2k / $3k / $4.5k+).",
            "Combine: best day ≤ 50% of total profit or keep trading until consistency clears.",
            "XFA Standard: 5 winning days of $150+ → withdraw ≤50% of balance, cap $5,000, keep 90%.",
            "XFA Consistency: ≥3 trading days + 40% consistency → withdraw ≤50%, cap $6,000, keep 90%.",
            "After any XFA payout, MLL locks at $0 (no cushion below breakeven).",
            f"Fees modeled in display only: Combine ${RULES.combine_fee:.0f} · Reset ${RULES.reset_fee:.0f} · XFA activation ${RULES.xfa_activation:.0f}.",
        ],
        "universe": {
            "start": str(prices.index[0].date()),
            "end": str(prices.index[-1].date()),
            "n_days": int(len(prices)),
        },
        "metrics": metrics,
        "combine": {
            "status": combine.status,
            "days": combine.days,
            "end_balance": round(combine.end_balance, 2),
            "min_balance": round(combine.min_balance, 2),
            "peak_balance": round(combine.peak_balance, 2),
            "best_day": round(combine.best_day, 2),
            "consistency_ratio": combine.consistency_ratio,
            "winning_days": combine.winning_days,
            "start": combine.start,
            "curve": _downsample_curve(combine.curve, 1),
        },
        "express_standard": {
            "status": xfa_std.status,
            "path": xfa_std.path,
            "days": xfa_std.days,
            "end_balance": round(xfa_std.end_balance, 2),
            "min_balance": round(xfa_std.min_balance, 2),
            "n_payouts": xfa_std.n_payouts,
            "locked_trader": round(xfa_std.locked_trader, 2),
            "locked_gross": round(xfa_std.locked_gross, 2),
            "start": xfa_std.start,
            "payouts": xfa_std.payouts,
            "curve": _downsample_curve(xfa_std.curve, 2),
        },
        "express_consistency": {
            "status": xfa_con.status,
            "path": xfa_con.path,
            "days": xfa_con.days,
            "end_balance": round(xfa_con.end_balance, 2),
            "min_balance": round(xfa_con.min_balance, 2),
            "n_payouts": xfa_con.n_payouts,
            "locked_trader": round(xfa_con.locked_trader, 2),
            "locked_gross": round(xfa_con.locked_gross, 2),
            "start": xfa_con.start,
            "payouts": xfa_con.payouts,
            "curve": _downsample_curve(xfa_con.curve, 2),
        },
        "random_start_combine": {
            **mc,
            "n_draws": MC_DRAWS,
            "seed": MC_SEED,
            "note": "Random Combine launches — fail = hit trailing $4,500 MLL.",
        },
        "express_from_combine_passes": {
            "n": len(xfa_from_passes),
            "mll_breach_rate": round(xfa_breach, 4),
            "avg_locked_trader": round(xfa_avg_locked, 2),
            "payout_hit_rate": round(xfa_pay_hit, 4),
            "path": "standard",
            "note": "Standard-path XFA started the day after random Combine passes.",
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT}")
    return payload


if __name__ == "__main__":
    main()
