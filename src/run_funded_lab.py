"""
Funded prop lab — shortlist firms for AI-agent trading and payout survival.

Produces site/data/funded_lab.json for site/funded-lab.html.

Important: prop rules change often. Treat this as a research checklist, not legal advice.
Verify each firm's current terms before paying a challenge fee.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.confluences import survival_score
from src.data import load_universe
from src.dd_methods import apply_dd_method
from src.metrics import equity_from_returns, summarize
from src.run_bakeoff import BASE_TECH_WEIGHT, HARD_MAX_DD, UNIVERSE
from src.strategies_a import allocate_residual_momentum, prepare_residual_momentum

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "funded_lab.json"

BASE_PARAMS = {
    "lookback_beta": 90,
    "formation": 63,
    "skip": 1,
    "n_tech": 4,
    "n_other": 4,
    "rebalance_every": 5,
    "cost_bps": 5.0,
    "tech_weight": BASE_TECH_WEIGHT,
}


# --- Firm catalog (research synthesis; verify before capital) ---
# Score weights: trust 25, api_ai 25, dd_model 25, payout_safety 25.
FIRMS: list[dict] = [
    {
        "id": "ftmo",
        "name": "FTMO",
        "tier": "primary",
        "asset_class": "Forex / CFD (incl. indices, metals, some stocks)",
        "backing_note": "Longest-running major retail prop brand; fee refund on first payout; large public payout history.",
        "automation": {
            "summary": "EAs on MT5 + cTrader Open API (C#/Python SDKs). Broadly allowed.",
            "api": "cTrader Open API / MT5 EA (not a first-party REST brokerage API)",
            "ai_agents": "Yes via EA or cTrader API — must avoid HFT / latency arb / toxic flow.",
            "restrictions": "No HFT, no latency arbitrage; news restricted on Normal funded accounts; strategy audits happen.",
        },
        "rules": {
            "eval": "2-step classic: ~10% then ~5% targets",
            "daily_loss": "5% of day-start balance",
            "max_dd": "10% static from initial balance",
            "dd_type": "static",
            "consistency": "None on standard 2-step (major payout advantage)",
            "min_days": "4 per phase",
            "payout": "On-demand after ~14 days from first funded trade; 80→90% split",
        },
        "scores": {"trust": 23, "api_ai": 21, "dd_model": 24, "payout_safety": 23},
        "fit_for_us": "Best default for our equity/CFD residual-mom agent: static DD, no consistency trap, mature automation path.",
        "watchouts": "Informal concentration reviews have denied some wildly one-day PnL profiles — still diversify winning days.",
        "links": {"site": "https://ftmo.com", "rules_hint": "Challenge / Funded Account rules"},
    },
    {
        "id": "e8",
        "name": "E8 Markets",
        "tier": "primary",
        "asset_class": "Forex / CFD",
        "backing_note": "Frequently ranked among more transparent CFD props; EAs allowed without pre-approval for standard strategies.",
        "automation": {
            "summary": "EAs / trade management across platforms; activity caps exist.",
            "api": "MT4/MT5 EA + cTrader path",
            "ai_agents": "Yes for standard algos; same EA across many accounts can trigger bans.",
            "restrictions": "~2,000 server requests/day caps in some plans; no HFT / latency arb; don't fingerprint-copy the same bot across lots of accounts.",
        },
        "rules": {
            "eval": "Flexible / often no hard time pressure (plan-dependent)",
            "daily_loss": "~5% (plan-dependent)",
            "max_dd": "~8% static (plan-dependent)",
            "dd_type": "static",
            "consistency": "Generally lighter than The5ers/FundedNext — verify per plan",
            "min_days": "Plan-dependent",
            "payout": "On-demand after initial waiting period (often ~14d); up to 100% split on some ladders",
        },
        "scores": {"trust": 19, "api_ai": 22, "dd_model": 22, "payout_safety": 19},
        "fit_for_us": "Strong algo runner-up when we want on-demand payouts and static DD tighter than 10%.",
        "watchouts": "Rule set is plan-heavy — lock the exact account type before coding risk limits.",
        "links": {"site": "https://e8markets.com", "rules_hint": "Account rules / prohibited strategies"},
    },
    {
        "id": "propr",
        "name": "Propr",
        "tier": "primary_ai_native",
        "asset_class": "Crypto/equity/FX perps (Hyperliquid) + predictions",
        "backing_note": "Onchain settlement + public payout explorer is unusual transparency; younger firm than FTMO — treat as higher platform risk.",
        "automation": {
            "summary": "First-party REST + Python/JS SDKs; marketed explicitly for AI agents.",
            "api": "Native REST API + SDKs",
            "ai_agents": "Best-in-class for Cursor-style agents (direct API, no MT bridge).",
            "restrictions": "Geo bans (US/UK/OFAC etc.); product is perps not cash equities.",
        },
        "rules": {
            "eval": "1-step / 2-step options; no time limit",
            "daily_loss": "~3% (plan-dependent)",
            "max_dd": "~3–6% static depending on plan",
            "dd_type": "static",
            "consistency": "None advertised",
            "min_days": "None",
            "payout": "On-demand USDC onchain; published tx hashes",
        },
        "scores": {"trust": 14, "api_ai": 25, "dd_model": 20, "payout_safety": 21},
        "fit_for_us": "Choose if we port the agent to perps and need a real API. Not a drop-in for Robinhood equities.",
        "watchouts": "Newer venue; tighter static DD; different market microstructure than residual-mom equities.",
        "links": {"site": "https://www.propr.xyz", "rules_hint": "Trading rules + API docs"},
    },
    {
        "id": "bulenox",
        "name": "Bulenox",
        "tier": "futures_algo",
        "asset_class": "CME futures",
        "backing_note": "One of the few futures props that openly markets full automation / third-party API.",
        "automation": {
            "summary": "NinjaScript + Rithmic R|API; third-party API usually paid monthly.",
            "api": "Rithmic R|API / NinjaTrader",
            "ai_agents": "Yes — full auto generally allowed (still no HFT/latency games).",
            "restrictions": "HFT / tick abuse banned; API connection fees; overnight limits vary by product.",
        },
        "rules": {
            "eval": "Futures eval / PA style",
            "daily_loss": "Plan-dependent",
            "max_dd": "Trailing styles common; some plans lock toward static",
            "dd_type": "trailing → may settle toward static (verify plan)",
            "consistency": "Often ~40% best-day share before payout (doesn't always breach — can block payout)",
            "min_days": "Often ~10 trading days before first payout",
            "payout": "Weekly / bi-weekly cycles common; first $10K often 100% on some marketing plans",
        },
        "scores": {"trust": 17, "api_ai": 23, "dd_model": 14, "payout_safety": 16},
        "fit_for_us": "Only if we rebuild as a futures strategy. Trailing + consistency need agent-level gates.",
        "watchouts": "Trailing DD fights momentum systems; consistency can delay payouts after a hot day.",
        "links": {"site": "https://bulenox.com", "rules_hint": "Automation / API fee / trailing DD FAQ"},
    },
    {
        "id": "mffu",
        "name": "MyFundedFutures",
        "tier": "futures_algo",
        "asset_class": "CME futures",
        "backing_note": "Strong Trustpilot reputation in futures props; updated policy to allow full automation (mid-2025+).",
        "automation": {
            "summary": "Full auto allowed on eval + funded; Tradovate / NinjaTrader / Rithmic stack.",
            "api": "Tradovate / Rithmic (platform APIs)",
            "ai_agents": "Yes if CME-compliant and not spamming (~200 trades/day soft ceiling reported).",
            "restrictions": "No latency arb / exchange-rule violations.",
        },
        "rules": {
            "eval": "Futures eval plans; some no daily loss limit",
            "daily_loss": "None on some plans (verify)",
            "max_dd": "Often EOD trailing",
            "dd_type": "trailing (EOD)",
            "consistency": "Plan-dependent; many futures firms use 30–40% best-day payout gates",
            "min_days": "Plan-dependent",
            "payout": "Fast cycles / next-day on some marketing; no activation fee on flagship pitches",
        },
        "scores": {"trust": 18, "api_ai": 22, "dd_model": 13, "payout_safety": 17},
        "fit_for_us": "Viable futures agent venue; trailing DD still a mismatch for equity RM as-is.",
        "watchouts": "Trailing DD + consistency can deny payouts even after 'winning'.",
        "links": {"site": "https://myfundedfutures.com", "rules_hint": "Automation policy update + trailing DD"},
    },
    {
        "id": "the5ers",
        "name": "The5ers",
        "tier": "secondary",
        "asset_class": "Forex / CFD",
        "backing_note": "High trust / long-term scaling reputation; slower / stricter risk box.",
        "automation": {
            "summary": "EAs allowed only if you own the source code.",
            "api": "MT5 / cTrader (with ownership constraint)",
            "ai_agents": "Yes if agent code is ours end-to-end — good cultural fit for in-house research.",
            "restrictions": "Purchased closed-source EAs are a ban risk; HFT/arb banned.",
        },
        "rules": {
            "eval": "Hyper Growth / High Stakes variants; ~6% targets",
            "daily_loss": "~4%",
            "max_dd": "~5–6% static (tight)",
            "dd_type": "static",
            "consistency": "Best day ≤ ~50% of profits (eval + funded)",
            "min_days": "Low / none on some plans",
            "payout": "Monthly; split scales toward 100% at high tiers",
        },
        "scores": {"trust": 22, "api_ai": 16, "dd_model": 15, "payout_safety": 15},
        "fit_for_us": "Only after we can run a much lower-vol book (CPPI / vol8 class).",
        "watchouts": "Tight DD + consistency make payout denial likely for juiced momentum days.",
        "links": {"site": "https://the5ers.com", "rules_hint": "Source-code ownership + consistency"},
    },
    {
        "id": "fundednext",
        "name": "FundedNext",
        "tier": "secondary",
        "asset_class": "Forex / CFD (+ futures arm)",
        "backing_note": "Large payout marketing presence; CFD automation is MT-only.",
        "automation": {
            "summary": "EAs on MT4/MT5 only; cTrader/Match-Trader manual-only on CFD.",
            "api": "MetaTrader EA path",
            "ai_agents": "Yes on MT; US traders may be blocked from MT → automation dead-end.",
            "restrictions": "Hyperactivity caps; banned strategy lists; news profit discounts on funded CFD.",
        },
        "rules": {
            "eval": "Often 8%/5% two-step (plan-dependent)",
            "daily_loss": "~5%",
            "max_dd": "~10% static",
            "dd_type": "static",
            "consistency": "Common 30–40% best-day rules on some models — payout blocker",
            "min_days": "~5 per phase",
            "payout": "Bi-weekly / monthly styles; high advertised splits",
        },
        "scores": {"trust": 17, "api_ai": 14, "dd_model": 21, "payout_safety": 12},
        "fit_for_us": "Usable if MT-hosted and we enforce consistency in the agent.",
        "watchouts": "Consistency + news profit haircuts are classic payout denial vectors.",
        "links": {"site": "https://fundednext.com", "rules_hint": "Prohibited strategies / MT-only automation"},
    },
]


AVOID: list[dict] = [
    {
        "name": "Apex Trader Funding (funded PA fully autonomous)",
        "reason": "Widely reported: fully autonomous set-and-forget bots restricted; semi-auto only on funded — poor fit for an unsupervised AI agent.",
    },
    {
        "name": "Take Profit Trader",
        "reason": "Explicit discretionary/no-bots posture in policy writeups — agent/API path is a denial risk.",
    },
    {
        "name": "Alpha Capital Group (full auto)",
        "reason": "Full automation typically banned; only trade-management EAs with pre-approval.",
    },
]


def _curve(rets: pd.Series, step: int = 5) -> list[dict]:
    eq = equity_from_returns(rets)
    if step > 1 and len(eq) > step * 2:
        idxs = list(range(0, len(eq), step))
        if idxs[-1] != len(eq) - 1:
            idxs.append(len(eq) - 1)
        eq = eq.iloc[idxs]
    return [
        {"date": dt.strftime("%Y-%m-%d"), "equity": round(float(val), 6)}
        for dt, val in eq.items()
    ]


def prop_risk_gate(
    rets: pd.Series,
    daily_loss_limit: float = 0.012,
    soft_dd: float = 0.06,
    hard_dd: float = 0.09,
    flatten_exp: float = 0.0,
) -> tuple[pd.Series, dict]:
    """
    Prop-compliant exposure overlay (lagged):
      - halt new risk after day P&L ≤ -daily_loss_limit (approx via overnight halt)
      - soft cut when path DD ≤ -soft_dd
      - flatten when path DD ≤ -hard_dd (buffer under a 10% static floor)
    """
    r = rets.fillna(0.0)
    eq = 1.0
    peak = 1.0
    day = None
    day_pnl = 0.0
    exp = 1.0
    out = []
    halts = softs = hards = 0

    for dt, ret in r.items():
        d = pd.Timestamp(dt).normalize()
        if day is None or d != day:
            day = d
            day_pnl = 0.0
            # reopen each day unless still under hard path DD
            if (eq / peak - 1.0) > -hard_dd:
                exp = 1.0 if (eq / peak - 1.0) > -soft_dd else 0.35

        traded = float(ret) * exp
        out.append(traded)
        eq *= 1.0 + traded
        peak = max(peak, eq)
        day_pnl += traded
        dd = eq / peak - 1.0

        if day_pnl <= -daily_loss_limit:
            exp = flatten_exp
            halts += 1
        elif dd <= -hard_dd:
            exp = flatten_exp
            hards += 1
        elif dd <= -soft_dd:
            exp = min(exp, 0.35)
            softs += 1

    series = pd.Series(out, index=r.index, name="prop_gated")
    stats = {
        "daily_halts": int(halts),
        "soft_dd_triggers": int(softs),
        "hard_dd_triggers": int(hards),
        "daily_loss_limit": daily_loss_limit,
        "soft_dd": soft_dd,
        "hard_dd": hard_dd,
    }
    return series, stats


def consistency_stats(rets: pd.Series) -> dict:
    """Proxy for best-day share of total positive profit (payout gate risk)."""
    daily = rets.fillna(0.0)
    pos = daily.clip(lower=0.0)
    total_pos = float(pos.sum())
    if total_pos <= 1e-12:
        return {"best_day_share": None, "positive_days": 0}
    best = float(pos.max())
    return {
        "best_day_share": best / total_pos,
        "positive_days": int((pos > 0).sum()),
        "best_day_pnl": best,
        "total_positive_pnl": total_pos,
    }


def run() -> dict:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    prices = load_universe(UNIVERSE, start="2018-01-01")
    prepared = prepare_residual_momentum(prices, **BASE_PARAMS)

    # Base books from our research stack
    v1, _ = allocate_residual_momentum(prepared, size_by_confidence=False)
    v2, v2_stats = allocate_residual_momentum(prepared, size_by_confidence=True)
    # Best DD survivor from dd-lab
    v2_corr_vol = apply_dd_method("dd_corr_vol10", v2, prices)
    # Prop-gated version of that survivor (FTMO-shaped buffers)
    prop_rets, gate_stats = prop_risk_gate(
        v2_corr_vol,
        daily_loss_limit=0.015,  # 1.5% day stop → buffer under 5% FTMO daily
        soft_dd=0.06,
        hard_dd=0.092,  # leave a little cushion under 10% static
    )

    books = []
    curves = {"spy": _curve(prices["SPY"].pct_change().fillna(0.0))}

    for key, label, thesis, series, extra in [
        (
            "v1",
            "Original Resid Mom",
            "Equal-weight Tech 80% — too wild for most prop DD boxes.",
            v1,
            {},
        ),
        (
            "v2",
            "Optimized V2",
            "Confidence sizing — still rejects a hard 35% retail gate, worse for 10% prop floors.",
            v2,
            {"avg_gross": v2_stats.get("avg_gross")},
        ),
        (
            "v2_corr_vol",
            "V2 + Anti-crowd + vol 10%",
            "Best dd-lab survivor historically — still size carefully for 5%/10% prop limits.",
            v2_corr_vol,
            {},
        ),
        (
            "prop_ftmo_template",
            "Prop-compliant agent (FTMO-shaped gates)",
            "Same signal as V2+anti-crowd+vol10, plus daily halt + soft/hard path DD buffers sized under 5%/10% static rules.",
            prop_rets,
            {"gate": gate_stats},
        ),
    ]:
        m = summarize(series, label)
        cons = consistency_stats(series)
        # Score with BOTH retail 35% gate and a prop-like 10% gate for comparison
        score_retail = survival_score(m, hard_max_dd=HARD_MAX_DD)
        score_prop10 = survival_score(m, hard_max_dd=0.10)
        row = {
            "key": key,
            "label": label,
            "thesis": thesis,
            "metrics": m,
            "consistency": cons,
            "score_retail_35": round(score_retail, 6),
            "score_prop_10": round(score_prop10, 6),
            "survived_retail_35": score_retail > -500,
            "survived_prop_10": score_prop10 > -500,
            "curve_key": key,
            **extra,
        }
        books.append(row)
        curves[key] = _curve(series)
        bds = cons.get("best_day_share")
        print(
            f"{key}: DD={m['max_dd']:.1%} Sharpe={m['sharpe']:.2f} "
            f"prop10={'OK' if row['survived_prop_10'] else 'REJECT'} "
            f"bestDay={'n/a' if bds is None else f'{bds:.1%}'}"
        )

    # Rank firms
    firms = []
    for f in FIRMS:
        total = sum(f["scores"].values())
        firms.append({**f, "total_score": total})
    firms.sort(key=lambda x: x["total_score"], reverse=True)
    for i, f in enumerate(firms, start=1):
        f["rank"] = i

    playbook = {
        "objective": "Pass eval + stay funded + get paid — without rule-denial on automation or consistency.",
        "recommended_firm": firms[0]["id"],
        "signal": "Optimized V2 residual momentum + anti-crowd corr + 10% vol target (from dd-lab).",
        "risk_box_ftmo_shaped": {
            "per_trade_risk": "≤0.5–0.75% of account (static DD grows only if you don't trail)",
            "daily_halt": "≤1.0–1.5% day loss (hard stop in agent before firm 5% trip)",
            "path_soft": "Cut exposure at ~5.5% path DD",
            "path_hard": "Flat by ~8.5% path DD (leave buffer under 10% static)",
            "consistency_self_rule": "Cap any day at ≤25–30% of MTD positive PnL even if firm has no rule",
            "news": "Stand down ± minutes around red-folder events on Normal FTMO",
            "automation_hygiene": "Own all code; no commercial 'challenge passer' EA fingerprints; stable IP/VPS; no copy-across-accounts",
            "trade_count": "Keep activity human-plausible — avoid hyperactivity / server spam caps",
        },
        "payout_checklist": [
            "Confirm automation clause on the exact account type (eval AND funded).",
            "Simulate static/trailing floor on your historical path before buying.",
            "Enforce daily halt in software — most breaches are daily, not max DD.",
            "Spread profits across days before requesting payout.",
            "Keep a written change-log of strategy versions (audit defense).",
            "Never run the identical closed-source bot on a web of borrowed accounts.",
        ],
    }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Independent research synthesis for our agent stack. Prop firm rules change without notice. "
            "Not an endorsement, solicitation, or guarantee of payouts. Verify current official rules "
            "before any challenge purchase."
        ),
        "rubric": {
            "trust": "Longevity, transparency, payout reputation, broker/backing signals (25)",
            "api_ai": "EA / Open API / native REST suitability for an unsupervised agent (25)",
            "dd_model": "Static vs trailing friendliness for residual-momentum paths (25)",
            "payout_safety": "Consistency rules, audit risk, news haircuts, denial vectors (25)",
        },
        "firms": firms,
        "avoid": AVOID,
        "strategy_books": books,
        "playbook": playbook,
        "curves": curves,
        "warnings": [
            "Retail prop trading has very low first-attempt pass rates industry-wide — size challenge fees as R&D cost.",
            "Trailing DD (many futures props) fights momentum systems; prefer static floors for our stack.",
            "Consistency rules don't always breach the account — they silently block payouts until diluted.",
            "Native AI REST APIs (e.g. Propr) are rare; most 'API' paths are MT5 EA or cTrader/Tradovate bridges.",
            "Our equity residual-mom research is closest to CFD index/stock products at FTMO/E8 — not a 1:1 Robinhood transfer.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT}")
    print("Top firms:", ", ".join(f"{f['rank']}. {f['name']} ({f['total_score']})" for f in firms[:4]))
    return payload


if __name__ == "__main__":
    run()
