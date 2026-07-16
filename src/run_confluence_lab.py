"""
Confluence boost lab — original RM vs optimized V2 vs 1.5× trade boosts.

Writes site/data/confluence_lab.json for site/confluence-lab.html.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.confluences import survival_score
from src.data import load_universe
from src.metrics import equity_from_returns, summarize
from src.name_confluences import (
    NAME_CONFLUENCES,
    STACK_SIGNAL_IDS,
    build_name_signal_panels,
    catalog_meta,
)
from src.run_bakeoff import BASE_TECH_WEIGHT, HARD_MAX_DD, UNIVERSE
from src.strategies_a import DEFAULT_V2_SIZE, allocate_residual_momentum, prepare_residual_momentum

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "confluence_lab.json"

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

BOOST_MULT = 1.5


def _curve(rets, step: int = 5) -> list[dict]:
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


def _book_row(key: str, label: str, thesis: str, rets, stats: dict) -> dict:
    m = summarize(rets, label)
    score = survival_score(m, hard_max_dd=HARD_MAX_DD)
    boost = stats.get("boost") or {}
    return {
        "key": key,
        "label": label,
        "thesis": thesis,
        "score": round(score, 6),
        "survived": score > -500,
        "metrics": m,
        "avg_gross": stats.get("avg_gross"),
        "boost_hit_rate": boost.get("hit_rate"),
        "boost_hits": boost.get("hits"),
        "boost_checks": boost.get("checks"),
        "n_trades": stats.get("n_trades"),
        "curve_key": key,
    }


def run() -> dict:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    prices = load_universe(UNIVERSE, start="2018-01-01")
    prepared = prepare_residual_momentum(prices, **BASE_PARAMS)
    panels = build_name_signal_panels(prices)

    # --- Core books ---
    orig_rets, orig_stats = allocate_residual_momentum(prepared, size_by_confidence=False)
    v2_rets, v2_stats = allocate_residual_momentum(prepared, size_by_confidence=True)

    # Confluence boost on original: curated stack ≥2 → 1.5×
    boost_rets, boost_stats = allocate_residual_momentum(
        prepared,
        size_by_confidence=False,
        boost_panels=panels,
        boost_mode="stack",
        boost_mult=BOOST_MULT,
        boost_min_count=2,
    )

    # Optimized V2 + stack boost
    v2_boost_rets, v2_boost_stats = allocate_residual_momentum(
        prepared,
        size_by_confidence=True,
        boost_panels=panels,
        boost_mode="stack",
        boost_mult=BOOST_MULT,
        boost_min_count=2,
    )

    stack_names = ", ".join(
        next(c.name for c in NAME_CONFLUENCES if c.id == sid) for sid in STACK_SIGNAL_IDS
    )

    books = [
        _book_row(
            "original",
            "Original Resid Mom (Tech 80%)",
            "Equal-weight within sleeves. The established baseline.",
            orig_rets,
            orig_stats,
        ),
        _book_row(
            "optimized_v2",
            "Optimized V2 (confidence sizing)",
            "Mild shrink-to-equal + confidence cash buffer (locked size cfg).",
            v2_rets,
            v2_stats,
        ),
        _book_row(
            "boost_any",
            f"Original + stacked confluence ×{BOOST_MULT:g}",
            f"Same names as original; if a name clears ≥2 of [{stack_names}], size ×{BOOST_MULT:g} then renormalize sleeve.",
            boost_rets,
            boost_stats,
        ),
        _book_row(
            "v2_boost_any",
            f"Optimized V2 + stacked confluence ×{BOOST_MULT:g}",
            f"V2 confidence sizing, then ×{BOOST_MULT:g} when ≥2 curated stack signals fire.",
            v2_boost_rets,
            v2_boost_stats,
        ),
    ]

    curves = {
        "original": _curve(orig_rets),
        "optimized_v2": _curve(v2_rets),
        "boost_any": _curve(boost_rets),
        "v2_boost_any": _curve(v2_boost_rets),
        "spy": _curve(prices["SPY"].pct_change().fillna(0.0)),
    }

    # --- Per-confluence tests (boost only when THAT signal fires) ---
    confluence_tests = []
    for nc in NAME_CONFLUENCES:
        rets, stats = allocate_residual_momentum(
            prepared,
            size_by_confidence=False,
            boost_panels=panels,
            boost_mode="single",
            boost_signal_id=nc.id,
            boost_mult=BOOST_MULT,
        )
        row = _book_row(
            f"boost_{nc.id}",
            f"×{BOOST_MULT:g} when {nc.name}",
            nc.thesis,
            rets,
            stats,
        )
        row["confluence_id"] = nc.id
        row["confluence_name"] = nc.name
        # Delta vs original
        row["delta_vs_original"] = {
            "score": row["score"] - books[0]["score"],
            "sharpe": row["metrics"]["sharpe"] - books[0]["metrics"]["sharpe"],
            "max_dd": row["metrics"]["max_dd"] - books[0]["metrics"]["max_dd"],
            "cagr": row["metrics"]["cagr"] - books[0]["metrics"]["cagr"],
        }
        confluence_tests.append(row)
        curves[row["curve_key"]] = _curve(rets)
        print(
            f"TEST {nc.id}: score={row['score']:.3f} hit={row['boost_hit_rate']} "
            f"Sharpe={row['metrics']['sharpe']:.2f} DD={row['metrics']['max_dd']:.1%}"
        )

    confluence_tests.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(confluence_tests, start=1):
        r["rank"] = i

    # Winner headline among core three (exclude v2_boost from primary trio ranking note)
    core = books[:3]
    core_ranked = sorted(core, key=lambda r: r["score"], reverse=True)

    # Recent boosted trades for table
    recent = [t for t in (boost_stats.get("trade_log") or []) if t.get("confluence_boost")][-40:]
    recent = list(reversed(recent))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Residual momentum — original vs optimized V2 vs confluence boost",
        "boost_mult": BOOST_MULT,
        "hard_max_dd": HARD_MAX_DD,
        "v2_size_cfg": dict(DEFAULT_V2_SIZE),
        "method": {
            "original": "Equal-weight within tech/non-tech sleeves (Tech 80%).",
            "optimized_v2": (
                "Locked confidence sizing: mild shrink-to-equal + cash buffer when "
                "mean confidence is weak."
            ),
            "boost": (
                f"At each rebalance, if a selected name clears ≥2 of the curated stack "
                f"({', '.join(STACK_SIGNAL_IDS)}), its sleeve weight is ×{BOOST_MULT:g}, "
                f"then the sleeve is renormalized. Below, each confluence is also tested alone at ×{BOOST_MULT:g}."
            ),
        },
        "boost_rule": {
            "mode": "stack",
            "min_count": 2,
            "mult": BOOST_MULT,
            "stack_signals": list(STACK_SIGNAL_IDS),
        },
        "name_confluence_catalog": catalog_meta(),
        "core_books": books,
        "core_winner": core_ranked[0]["key"],
        "confluence_tests": confluence_tests,
        "curves": curves,
        "recent_boosted_trades": recent,
        "warnings": [
            "Long-only residual momentum, Tech 80% sleeve — no shorts.",
            f"Confluence boost = ×{BOOST_MULT:g} when ≥2 curated stack signals fire "
            f"({', '.join(STACK_SIGNAL_IDS)}); single-signal tables test each confluence alone.",
            "Signals are lag-1 (prior close) to avoid look-ahead.",
            "Hard MaxDD gate in scores: reject if |MaxDD| > 35%.",
            f"Best single-confluence boost: {confluence_tests[0]['confluence_name']} "
            f"(score={confluence_tests[0]['score']:.3f}).",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT}")
    for b in books:
        print(
            f"BOOK {b['key']}: score={b['score']:.3f} Sharpe={b['metrics']['sharpe']:.2f} "
            f"CAGR={b['metrics']['cagr']:.1%} DD={b['metrics']['max_dd']:.1%} "
            f"hit={b.get('boost_hit_rate')}"
        )
    return payload


if __name__ == "__main__":
    run()
