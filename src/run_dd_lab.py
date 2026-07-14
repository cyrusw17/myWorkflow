"""
Drawdown lab — fix Optimized V2 MaxDD with systematic overlays.

Base = locked Optimized V2 confidence sizing (rejects alone at ~−46% DD).
Tries existing confluence overlays + dedicated DD methods + tighter V2 cash buffers.
Writes site/data/dd_lab.json for site/dd-lab.html.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.confluences import survival_score
from src.data import load_universe
from src.dd_methods import DD_METHODS, apply_dd_method, catalog_meta
from src.metrics import equity_from_returns, summarize
from src.run_bakeoff import BASE_TECH_WEIGHT, HARD_MAX_DD, UNIVERSE
from src.strategies_a import (
    DEFAULT_V2_SIZE,
    allocate_residual_momentum,
    prepare_residual_momentum,
)

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
OUT = SITE_DATA / "dd_lab.json"

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

# Extra V2 cash-buffer variants aimed at cutting raw MaxDD before overlays.
TIGHT_V2_CFGS: list[dict] = [
    {
        "name": "v2_tight_cash_A",
        "label": "V2 tighter cash (floor 0.25 / 55–75)",
        "size_cfg": {**DEFAULT_V2_SIZE, "gross_floor": 0.25, "conf_lo": 55.0, "conf_hi": 75.0},
    },
    {
        "name": "v2_tight_cash_B",
        "label": "V2 defensive cash (floor 0.20 / 58–80)",
        "size_cfg": {
            **DEFAULT_V2_SIZE,
            "gross_floor": 0.20,
            "conf_lo": 58.0,
            "conf_hi": 80.0,
            "shrink": 0.95,
        },
    },
    {
        "name": "v2_tight_cash_C",
        "label": "V2 deep buffer (floor 0.15 / 60–82)",
        "size_cfg": {
            **DEFAULT_V2_SIZE,
            "gross_floor": 0.15,
            "conf_lo": 60.0,
            "conf_hi": 82.0,
            "shrink": 0.95,
            "power": 0.15,
        },
    },
]


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


def _row(key: str, label: str, family: str, thesis: str, rets, extra: dict | None = None) -> dict:
    m = summarize(rets, label)
    score = survival_score(m, hard_max_dd=HARD_MAX_DD)
    out = {
        "key": key,
        "label": label,
        "family": family,
        "thesis": thesis,
        "score": round(score, 6),
        "survived": score > -500,
        "metrics": m,
        "curve_key": key,
    }
    if extra:
        out.update(extra)
    return out


def run() -> dict:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    prices = load_universe(UNIVERSE, start="2018-01-01")
    prepared = prepare_residual_momentum(prices, **BASE_PARAMS)

    # Baselines
    v1_rets, _ = allocate_residual_momentum(prepared, size_by_confidence=False)
    v2_rets, v2_stats = allocate_residual_momentum(prepared, size_by_confidence=True)

    rows: list[dict] = []
    curves = {
        "spy": _curve(prices["SPY"].pct_change().fillna(0.0)),
        "original_v1": _curve(v1_rets),
        "optimized_v2": _curve(v2_rets),
    }

    rows.append(
        _row(
            "original_v1",
            "Original Resid Mom (equal-weight)",
            "baseline",
            "Equal-weight Tech 80% — reference only.",
            v1_rets,
        )
    )
    rows.append(
        _row(
            "optimized_v2",
            "Optimized V2 (confidence sizing)",
            "baseline",
            "Locked shrink-to-equal + confidence cash buffer. Needs DD fix.",
            v2_rets,
            {"avg_gross": v2_stats.get("avg_gross"), "size_cfg": dict(DEFAULT_V2_SIZE)},
        )
    )

    # Tighter V2 cash variants (re-allocate)
    for cfg in TIGHT_V2_CFGS:
        size_cfg = dict(cfg["size_cfg"])
        rets, stats = allocate_residual_momentum(
            prepared, size_by_confidence=True, size_cfg=size_cfg
        )
        key = cfg["name"]
        row = _row(
            key,
            cfg["label"],
            "tight_v2_cash",
            "More aggressive confidence→cash mapping to pre-empt drawdowns.",
            rets,
            {"avg_gross": stats.get("avg_gross"), "size_cfg": size_cfg},
        )
        rows.append(row)
        curves[key] = _curve(rets)
        print(
            f"CASH {key}: score={row['score']:.3f} DD={row['metrics']['max_dd']:.1%} "
            f"Sharpe={row['metrics']['sharpe']:.2f} gross={stats.get('avg_gross')}"
        )

    # Overlay methods on locked Optimized V2
    for method in DD_METHODS:
        rets = apply_dd_method(method.id, v2_rets, prices)
        key = method.id
        row = _row(
            key,
            f"V2 + {method.name}",
            method.family,
            method.thesis,
            rets,
        )
        rows.append(row)
        curves[key] = _curve(rets)
        flag = "OK" if row["survived"] else "REJECT"
        print(
            f"{flag} {method.id}: score={row['score']:.3f} DD={row['metrics']['max_dd']:.1%} "
            f"Sharpe={row['metrics']['sharpe']:.2f} CAGR={row['metrics']['cagr']:.1%}"
        )

    # Also: best practice — apply top DD methods on tight cash V2 if any tight survived raw
    survivors = [r for r in rows if r["survived"] and r["family"] != "baseline"]
    survivors.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(survivors, start=1):
        r["rank"] = i

    all_sorted = sorted(rows, key=lambda r: (r["survived"], r["score"]), reverse=True)
    for i, r in enumerate(all_sorted, start=1):
        r["rank_all"] = i

    best = survivors[0] if survivors else None
    top_show = (survivors or all_sorted)[:8]

    # Near-misses: rejected but closest to 35% gate (useful quant diagnostics)
    rejects = [r for r in rows if not r["survived"] and r["key"] != "original_v1"]
    rejects.sort(key=lambda r: abs(r["metrics"]["max_dd"]))
    near = rejects[:5]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Fix Optimized V2 drawdown — method bake-off",
        "hard_max_dd": HARD_MAX_DD,
        "base": {
            "label": "Optimized V2 (confidence sizing)",
            "size_cfg": dict(DEFAULT_V2_SIZE),
            "avg_gross": v2_stats.get("avg_gross"),
            "max_dd": rows[1]["metrics"]["max_dd"],
            "sharpe": rows[1]["metrics"]["sharpe"],
            "cagr": rows[1]["metrics"]["cagr"],
            "score": rows[1]["score"],
            "note": (
                "Bare Optimized V2 fails the MaxDD≤35% retail gate (~−46%). "
                "This lab searches overlays / cash tweaks that clear the gate."
            ),
        },
        "methods_tested": len(rows) - 2,
        "survivors": len(survivors),
        "best": best,
        "top": top_show,
        "near_misses": near,
        "all": all_sorted,
        "catalog": catalog_meta(),
        "curves": {
            "spy": curves["spy"],
            "optimized_v2": curves["optimized_v2"],
            "original_v1": curves["original_v1"],
            **{r["curve_key"]: curves[r["curve_key"]] for r in top_show if r["curve_key"] in curves},
            **{r["curve_key"]: curves[r["curve_key"]] for r in near if r["curve_key"] in curves},
        },
        "warnings": [
            "Hard gate: reject if |MaxDD| > 35% (account survival).",
            "Base book is locked Optimized V2 confidence sizing.",
            f"Tested {len(rows) - 2} DD-control variants (confluences + dedicated methods + tight cash).",
            f"Survivors: {len(survivors)}.",
            (
                f"Best: {best['label']} (score={best['score']:.3f}, MaxDD={best['metrics']['max_dd']:.1%})."
                if best
                else "No survivor cleared the 35% MaxDD gate — see near-misses."
            ),
            "Long-only — no shorts.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"\nWrote {OUT}")
    print(f"Survivors {len(survivors)}/{len(rows)-2}")
    if best:
        print(f"BEST {best['label']} score={best['score']:.3f} DD={best['metrics']['max_dd']:.1%}")
    return payload


if __name__ == "__main__":
    run()
