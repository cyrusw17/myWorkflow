from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.confluences import CONFLUENCES, apply_confluence, catalog_meta, survival_score
from src.data import fetch_ohlc, load_universe
from src.metrics import equity_from_returns, summarize, vol_target_returns
from src.strategies_a import TECH_TICKERS, residual_momentum_returns
from src.strategies_b import lsc_proxy_returns

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
EVENTS = ROOT / "outputs" / "lsc_events.csv"
CONF_OUT = ROOT / "outputs" / "confluence_bakeoff.json"
V2_OUT = ROOT / "outputs" / "v1_v2_compare.json"

UNIVERSE = [
    "SPY",
    "XLK",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AVGO",
    "AMD",
    "CRM",
    "ORCL",
    "ADBE",
    "CSCO",
    "INTC",
    "TXN",
    "QCOM",
    "AMAT",
    "META",
    "GOOGL",
    "AMZN",
    "MU",
    "NOW",
    "IWM",
    "XLF",
    "XLE",
    "XLV",
    "XLI",
    "XLY",
    "XLP",
    "XLU",
    "GLD",
    "TLT",
    "JPM",
    "JNJ",
    "XOM",
    "WMT",
    "PG",
    "KO",
    "BAC",
    "UNH",
    "HD",
    "V",
    "MA",
    "DIS",
    "CAT",
    "BA",
]

BASE_TECH_WEIGHT = 0.80
HARD_MAX_DD = 0.35
TOP_N_SHOW = 4


def _curve(rets: pd.Series, step: int = 5) -> list[dict]:
    """Equity path for charts. step>1 thins points to keep bakeoff.json small."""
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


def _pair_row(sid: str, label: str, thesis: str, m1: dict, m2: dict, s1: float, s2: float) -> dict:
    v1_key = "conf_base" if sid == "base" else f"conf_{sid}"
    v2_key = "v2_base" if sid == "base" else f"v2_{sid}"
    return {
        "id": sid,
        "label": label,
        "thesis": thesis,
        "v1": {
            "score": round(s1, 6),
            "survived": s1 > -500,
            "cagr": m1["cagr"],
            "sharpe": m1["sharpe"],
            "sortino": m1["sortino"],
            "max_dd": m1["max_dd"],
            "calmar": m1["calmar"],
            "curve_key": v1_key,
        },
        "v2": {
            "score": round(s2, 6),
            "survived": s2 > -500,
            "cagr": m2["cagr"],
            "sharpe": m2["sharpe"],
            "sortino": m2["sortino"],
            "max_dd": m2["max_dd"],
            "calmar": m2["calmar"],
            "curve_key": v2_key,
        },
        "delta": {
            "score": round(s2 - s1, 6),
            "cagr": m2["cagr"] - m1["cagr"],
            "sharpe": m2["sharpe"] - m1["sharpe"],
            "max_dd": m2["max_dd"] - m1["max_dd"],  # less negative is better
            "calmar": m2["calmar"] - m1["calmar"],
        },
        "winner": "v2" if s2 > s1 else ("v1" if s1 > s2 else "tie"),
    }


def run() -> dict:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)

    prices = load_universe(UNIVERSE, start="2018-01-01")
    spy_ohlc = fetch_ohlc("SPY", start="2018-01-01").reindex(prices.index).ffill()
    spy_rets = prices["SPY"].pct_change().fillna(0.0)

    base_params = {
        "lookback_beta": 90,
        "formation": 63,
        "skip": 1,
        "n_tech": 4,
        "n_other": 4,
        "rebalance_every": 5,
        "cost_bps": 5.0,
        "tech_weight": BASE_TECH_WEIGHT,
    }

    # --- V1 equal-weight (unchanged) ---
    base_rets_v1, base_stats_v1 = residual_momentum_returns(
        prices, size_by_confidence=False, **base_params
    )
    base_curve_fingerprint = [
        round(float(v), 8) for v in equity_from_returns(base_rets_v1).iloc[::21].tolist()[:40]
    ]

    # --- V2 confidence-sized holdings ---
    base_rets_v2, base_stats_v2 = residual_momentum_returns(
        prices, size_by_confidence=True, **base_params
    )

    trade_log = list(base_stats_v1.get("trade_log") or [])
    conf_summary = dict(base_stats_v1.get("confidence") or {})

    curves: dict[str, list[dict]] = {}
    pairs: list[dict] = []

    def _eval_family(base_rets: pd.Series, version: str) -> tuple[list[dict], dict[str, pd.Series], dict[str, list[dict]]]:
        local_rows: list[dict] = []
        local_rets: dict[str, pd.Series] = {"base": base_rets}
        local_curves: dict[str, list[dict]] = {}

        m0 = summarize(base_rets, f"{version} Base Tech 80%")
        s0 = survival_score(m0, hard_max_dd=HARD_MAX_DD)
        base_key = "conf_base" if version == "v1" else "v2_base"
        local_rows.append(
            {
                "id": "base",
                "label": "Base Tech 80% (no confluence)",
                "thesis": "Residual momentum with 80% tech long sleeve; no overlay.",
                "score": round(s0, 6),
                "survived": s0 > -500,
                "metrics": m0,
                "curve_key": base_key,
            }
        )
        local_curves[base_key] = _curve(base_rets)

        print(
            f"{version.upper()} BASE: score={s0:.3f} Sharpe={m0['sharpe']:.2f} "
            f"CAGR={m0['cagr']:.2%} MaxDD={m0['max_dd']:.2%}"
        )

        for conf in CONFLUENCES:
            rets = apply_confluence(conf.id, base_rets, prices)
            metrics = summarize(rets, f"{version} {conf.name}")
            score = survival_score(metrics, hard_max_dd=HARD_MAX_DD)
            key = f"conf_{conf.id}" if version == "v1" else f"v2_{conf.id}"
            row = {
                "id": conf.id,
                "label": conf.name,
                "thesis": conf.thesis,
                "score": round(score, 6),
                "survived": score > -500,
                "metrics": metrics,
                "curve_key": key,
            }
            local_rows.append(row)
            local_curves[key] = _curve(rets)
            local_rets[conf.id] = rets
            flag = "OK" if row["survived"] else "REJECT"
            print(
                f"{version.upper()} {flag} {conf.id}: score={score:.3f} "
                f"Sharpe={metrics['sharpe']:.2f} CAGR={metrics['cagr']:.2%} MaxDD={metrics['max_dd']:.2%}"
            )
        return local_rows, local_rets, local_curves

    rows_v1, rets_map_v1, curves_v1 = _eval_family(base_rets_v1, "v1")
    rows_v2, _rets_map_v2, curves_v2 = _eval_family(base_rets_v2, "v2")
    curves.update(curves_v1)
    curves.update(curves_v2)

    # Pairwise v1 vs v2 for base + every confluence
    by_id_v1 = {r["id"]: r for r in rows_v1}
    by_id_v2 = {r["id"]: r for r in rows_v2}
    for sid in ["base"] + [c.id for c in CONFLUENCES]:
        r1 = by_id_v1[sid]
        r2 = by_id_v2[sid]
        pair = _pair_row(
            sid,
            r1["label"],
            r1["thesis"],
            r1["metrics"],
            r2["metrics"],
            r1["score"],
            r2["score"],
        )
        pairs.append(pair)
        print(
            f"PAIR {sid}: winner={pair['winner']} Δscore={pair['delta']['score']:+.3f} "
            f"v1DD={r1['metrics']['max_dd']:.1%} v2DD={r2['metrics']['max_dd']:.1%}"
        )

    # Rank V1 family for Strat A selection (preserve prior behavior)
    ranked = sorted(rows_v1, key=lambda r: r["score"], reverse=True)
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i
    survivors = [r for r in ranked if r["survived"]]
    top = (survivors or ranked)[:TOP_N_SHOW]
    best = top[0]
    a_rets = rets_map_v1["base" if best["id"] == "base" else best["id"]]

    b_rets, events = lsc_proxy_returns(spy_ohlc)
    events.to_csv(EVENTS, index=False)

    idx = spy_rets.index.intersection(a_rets.index).intersection(b_rets.index)
    spy_rets = spy_rets.loc[idx]
    a_rets = a_rets.loc[idx]
    b_rets = b_rets.loc[idx]

    a_vol = float(a_rets.std() * (252 ** 0.5))
    spy_vm = vol_target_returns(spy_rets, target_vol=max(a_vol, 0.05))

    metrics = [
        summarize(spy_rets, "SPY B&H"),
        summarize(spy_vm, "SPY vol-match"),
        summarize(a_rets, f"Strat A · {best['label']}"),
        summarize(b_rets, "Strat B LSC proxy"),
    ]

    if metrics[2]["sharpe"] > metrics[1]["sharpe"] and abs(metrics[2]["max_dd"]) <= HARD_MAX_DD:
        decision = "SHIP_A_PAPER"
    elif metrics[3]["sharpe"] > metrics[0]["sharpe"] and metrics[3]["sharpe"] > 0:
        decision = "SHIP_B_PAPER"
    else:
        decision = "KILL_REDESIGN"

    top_payload = [
        {
            "rank": r["rank"],
            "id": r["id"],
            "label": r["label"],
            "thesis": r["thesis"],
            "score": r["score"],
            "survived": r["survived"],
            "curve_key": r["curve_key"],
            "cagr": r["metrics"]["cagr"],
            "sharpe": r["metrics"]["sharpe"],
            "sortino": r["metrics"]["sortino"],
            "max_dd": r["metrics"]["max_dd"],
            "calmar": r["metrics"]["calmar"],
        }
        for r in top
    ]

    pairs_sorted = sorted(pairs, key=lambda p: p["v2"]["score"], reverse=True)
    v2_wins = sum(1 for p in pairs if p["winner"] == "v2")
    v1_wins = sum(1 for p in pairs if p["winner"] == "v1")

    CONF_OUT.write_text(json.dumps({"ranked_v1": ranked, "top_v1": top_payload}, indent=2, default=str))
    V2_OUT.write_text(json.dumps({"pairs": pairs_sorted, "v1_wins": v1_wins, "v2_wins": v2_wins}, indent=2))

    post_fingerprint = [
        round(float(v), 8) for v in equity_from_returns(base_rets_v1).iloc[::21].tolist()[:40]
    ]
    if post_fingerprint != base_curve_fingerprint:
        raise RuntimeError("V1 base equity curve drifted unexpectedly")

    recent_trades = trade_log[-60:]
    (ROOT / "outputs" / "trade_confidence.json").write_text(
        json.dumps({"summary": conf_summary, "n_trades": len(trade_log), "trades": trade_log}, indent=2)
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "yahoo finance chart API (daily OHLC, cached)",
        "universe": UNIVERSE,
        "assumptions": {
            "start": "2018-01-01",
            "cost_bps_per_turnover_or_entry": 5.0,
            "strategy_a": {
                "mode": "residual_momentum_plus_confluence",
                **{k: v for k, v in base_params.items() if k != "cost_bps"},
                "tech_tickers": sorted(t for t in TECH_TICKERS if t in UNIVERSE),
                "base_tech_weight": BASE_TECH_WEIGHT,
                "selected_confluence": best["id"],
                "selected_label": best["label"],
                "selected_score": best["score"],
                "hard_max_dd": HARD_MAX_DD,
                "score_method": (
                    f"survival: reject |MaxDD|>{int(HARD_MAX_DD*100)}%; else "
                    "0.40*Calmar + 0.30*Sortino + 0.20*Sharpe + 0.10*CAGR_term"
                ),
                "confluences_tested": len(CONFLUENCES),
                "candidates_including_base": len(rows_v1),
                "survivors": len(survivors),
                "v1_note": "Equal-weight within sleeves; confidence is diagnostic only.",
                "v2_note": "Same names; holdings sized by confidence within each sleeve.",
            },
            "strategy_b": {
                "note": "Daily LSC proxy until 5m/1H stack is wired",
                "lookback_pool": 20,
                "hold_days": 5,
                "buffer": 0.001,
            },
            "starting_equity": 1.0,
        },
        "metrics": metrics,
        "decision_status": decision,
        "curves": {
            "spy_bh": _curve(spy_rets),
            "spy_vol_match": _curve(spy_vm),
            "strat_a": _curve(a_rets),
            "strat_b": _curve(b_rets),
            **curves,
        },
        "confluence_bakeoff": {
            "hard_max_dd": HARD_MAX_DD,
            "catalog": catalog_meta(),
            "survivors": len(survivors),
            "tested": len(rows_v1),
            "top": top_payload,
        },
        "v1_v2_compare": {
            "method": (
                "V1 equal-weight sleeves; V2 confidence-weighted holdings within sleeves "
                "(same tickers / rebalance schedule / tech sleeve %). Same confluence overlays applied to both."
            ),
            "v1_wins": v1_wins,
            "v2_wins": v2_wins,
            "ties": len(pairs) - v1_wins - v2_wins,
            "pairs": pairs_sorted,
        },
        "trade_confidence": {
            "summary": conf_summary,
            "n_trades": len(trade_log),
            "recent_trades": recent_trades,
            "v2_summary": base_stats_v2.get("confidence"),
        },
        "lsc_event_count": int(len(events)),
        "warnings": [
            f"Base book = residual momentum @ {int(BASE_TECH_WEIGHT*100)}% tech (long-only).",
            "V1 keeps equal sleeve weights; V2 sizes holdings by confidence (same names).",
            f"Tested {len(CONFLUENCES)} confluence overlays + base on both V1 and V2.",
            f"Pairwise scoreboard: V2 wins {v2_wins}, V1 wins {v1_wins}.",
            "Strategy B is a daily sweep/reclaim proxy — not the full 5m ICT confluence engine yet.",
            "Interim decision only — not live capital advice.",
            f"Selected Strat A (from V1 survival rank): {best['label']} (score={best['score']:.3f}).",
        ],
    }

    out = SITE_DATA / "bakeoff.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"Decision (interim): {decision}")
    print(f"V1 survivors: {len(survivors)}/{len(rows_v1)}")
    print(f"V1 vs V2 scoreboard: v2_wins={v2_wins} v1_wins={v1_wins}")
    return payload


if __name__ == "__main__":
    run()
