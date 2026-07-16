"""
Sweep V2 confidence-sizing params for drawdown-efficient portfolio construction.

Two-stage:
  A) coarse screen on base residual-momentum book (fast filter via prepared picks)
  B) full confluence family on top candidates vs frozen V1

Writes outputs/v2_size_sweep.json and prints the locked winner.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from src.confluences import CONFLUENCES, apply_confluence, survival_score
from src.data import load_universe
from src.metrics import summarize
from src.run_bakeoff import BASE_TECH_WEIGHT, HARD_MAX_DD, UNIVERSE
from src.strategies_a import allocate_residual_momentum, prepare_residual_momentum

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "v2_size_sweep.json"

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


def _family_scores(base_rets, prices):
    rows = []
    m0 = summarize(base_rets, "base")
    s0 = survival_score(m0, hard_max_dd=HARD_MAX_DD)
    rows.append({"id": "base", "score": s0, "metrics": m0, "survived": s0 > -500})
    for conf in CONFLUENCES:
        rets = apply_confluence(conf.id, base_rets, prices)
        m = summarize(rets, conf.name)
        s = survival_score(m, hard_max_dd=HARD_MAX_DD)
        rows.append({"id": conf.id, "score": s, "metrics": m, "survived": s > -500})
    return rows


def _objective(rows_v2, rows_v1) -> dict:
    by1 = {r["id"]: r for r in rows_v1}
    wins = ties = 0
    deltas = []
    for r2 in rows_v2:
        r1 = by1[r2["id"]]
        d = r2["score"] - r1["score"]
        deltas.append(d)
        if d > 1e-12:
            wins += 1
        elif abs(d) <= 1e-12:
            ties += 1
    survivors = [r for r in rows_v2 if r["survived"]]
    mean_surv = float(sum(r["score"] for r in survivors) / len(survivors)) if survivors else -999.0
    best = max((r["score"] for r in survivors), default=-999.0)
    mean_all = float(sum(r["score"] for r in rows_v2) / len(rows_v2))
    obj = (
        2.0 * mean_surv
        + 1.2 * best
        + 0.8 * (len(survivors) / len(rows_v2))
        + 0.35 * wins
        + 0.15 * float(sum(deltas) / len(deltas))
        + 0.05 * mean_all
    )
    return {
        "objective": round(obj, 6),
        "survivors": len(survivors),
        "tested": len(rows_v2),
        "mean_survivor_score": round(mean_surv, 6),
        "best_survivor_score": round(best, 6),
        "v2_wins": wins,
        "ties": ties,
        "v1_wins": len(rows_v2) - wins - ties,
        "mean_delta": round(float(sum(deltas) / len(deltas)), 6),
    }


def _base_screen_score(metrics: dict, avg_gross: float | None) -> float:
    mdd = abs(float(metrics["max_dd"]))
    sharpe = float(metrics["sharpe"])
    calmar = float(metrics["calmar"])
    cagr = float(metrics["cagr"])
    gross = float(avg_gross or 1.0)
    cash_pen = 1.0 - max(0.55 - gross, 0.0) * 1.5
    dd_term = 1.0 / (1.0 + max(mdd - 0.18, 0.0) * 5.0)
    return (0.45 * calmar + 0.30 * sharpe + 0.15 * max(cagr, 0.0) * 4.0 + 0.10 * gross) * dd_term * cash_pen


def stage_a_grid() -> list[dict]:
    cfgs = [
        {
            "name": "naive_linear",
            "power": 1.0,
            "shrink": 0.0,
            "floor": 5.0,
            "max_name_frac": 1.0,
            "gross_mode": "full",
            "gross_floor": 1.0,
            "gross_ceil": 1.0,
            "conf_lo": 40.0,
            "conf_hi": 75.0,
        }
    ]
    for power, shrink, max_frac, g_floor, conf_lo in itertools.product(
        [0.4, 0.65, 0.9],
        [0.45, 0.65, 0.80],
        [0.34, 0.42],
        [0.45, 0.55, 0.65],
        [40.0, 48.0],
    ):
        conf_hi = 72.0 if conf_lo <= 42 else 78.0
        cfgs.append(
            {
                "name": f"g_p{power}_s{shrink}_m{max_frac}_f{g_floor}_{conf_lo}-{conf_hi}",
                "power": power,
                "shrink": shrink,
                "floor": 12.0,
                "max_name_frac": max_frac,
                "gross_mode": "conf_mean",
                "gross_floor": g_floor,
                "gross_ceil": 1.0,
                "conf_lo": conf_lo,
                "conf_hi": conf_hi,
            }
        )
    for power, shrink, max_frac in itertools.product(
        [0.5, 0.75, 1.0],
        [0.55, 0.75, 0.9],
        [0.35, 0.42],
    ):
        cfgs.append(
            {
                "name": f"full_p{power}_s{shrink}_m{max_frac}",
                "power": power,
                "shrink": shrink,
                "floor": 12.0,
                "max_name_frac": max_frac,
                "gross_mode": "full",
                "gross_floor": 1.0,
                "gross_ceil": 1.0,
                "conf_lo": 40.0,
                "conf_hi": 75.0,
            }
        )
    seen = set()
    uniq = []
    for c in cfgs:
        key = tuple(sorted((k, v) for k, v in c.items() if k != "name"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return uniq


def run(stage_b_keep: int = 12) -> dict:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prices = load_universe(UNIVERSE, start="2018-01-01")

    print("Preparing residual book once…")
    prepared = prepare_residual_momentum(prices, **BASE_PARAMS)

    print("Frozen V1 family…")
    v1_rets, _ = allocate_residual_momentum(prepared, size_by_confidence=False)
    rows_v1 = _family_scores(v1_rets, prices)
    v1_sum = _objective(rows_v1, rows_v1)
    print(f"V1 survivors={v1_sum['survivors']} mean_surv={v1_sum['mean_survivor_score']:.3f}")

    cfgs = stage_a_grid()
    print(f"Stage A: screening {len(cfgs)} configs on base book…")
    stage_a = []
    for i, cfg in enumerate(cfgs, start=1):
        rets, stats = allocate_residual_momentum(
            prepared, size_by_confidence=True, size_cfg=cfg
        )
        m = summarize(rets, cfg["name"])
        screen = _base_screen_score(m, stats.get("avg_gross"))
        stage_a.append(
            {
                "cfg": cfg,
                "screen": round(screen, 6),
                "avg_gross": stats.get("avg_gross"),
                "base_metrics": m,
                "rets": rets,
            }
        )
        if i % 10 == 0 or i == len(cfgs):
            print(
                f"A[{i}/{len(cfgs)}] latest screen={screen:.3f} DD={m['max_dd']:.1%} "
                f"gross={stats.get('avg_gross')}"
            )

    stage_a.sort(key=lambda r: r["screen"], reverse=True)
    finalists = stage_a[:stage_b_keep]
    if not any(f["cfg"]["name"] == "naive_linear" for f in finalists):
        naive = next(r for r in stage_a if r["cfg"]["name"] == "naive_linear")
        finalists.append(naive)

    print(f"\nStage B: full confluence bake-off on {len(finalists)} finalists…")
    results = []
    for i, cand in enumerate(finalists, start=1):
        rows = _family_scores(cand["rets"], prices)
        summary = _objective(rows, rows_v1)
        base_m = cand["base_metrics"]
        row = {
            "cfg": cand["cfg"],
            "avg_gross": cand["avg_gross"],
            "stage_a_screen": cand["screen"],
            "base_sharpe": base_m["sharpe"],
            "base_max_dd": base_m["max_dd"],
            "base_cagr": base_m["cagr"],
            **summary,
        }
        results.append(row)
        print(
            f"B[{i}/{len(finalists)}] obj={row['objective']:.3f} surv={row['survivors']} "
            f"wins={row['v2_wins']} meanΔ={row['mean_delta']:+.3f} · {cand['cfg']['name']}"
        )

    results.sort(key=lambda r: (r["objective"], r["survivors"], r["v2_wins"]), reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    stage_a_lite = [
        {
            "cfg": r["cfg"],
            "screen": r["screen"],
            "avg_gross": r["avg_gross"],
            "base_sharpe": r["base_metrics"]["sharpe"],
            "base_max_dd": r["base_metrics"]["max_dd"],
            "base_cagr": r["base_metrics"]["cagr"],
        }
        for r in stage_a
    ]

    payload = {
        "hard_max_dd": HARD_MAX_DD,
        "objective_note": (
            "2*mean_survivor + 1.2*best_survivor + 0.8*survivor_rate + 0.35*v2_wins "
            "+ 0.15*mean_delta + 0.05*mean_all"
        ),
        "v1_baseline": {
            "survivors": v1_sum["survivors"],
            "mean_survivor_score": v1_sum["mean_survivor_score"],
            "best_survivor_score": v1_sum["best_survivor_score"],
        },
        "n_stage_a": len(stage_a_lite),
        "n_stage_b": len(results),
        "best": results[0],
        "stage_b": results,
        "stage_a_top20": stage_a_lite[:20],
    }
    OUT.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nWrote {OUT}")
    print("BEST CFG:", json.dumps(results[0]["cfg"], indent=2))
    print(
        f"obj={results[0]['objective']:.3f} survivors={results[0]['survivors']} "
        f"v2_wins={results[0]['v2_wins']} mean_surv={results[0]['mean_survivor_score']:.3f}"
    )
    return payload


if __name__ == "__main__":
    run()
