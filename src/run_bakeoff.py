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

# Locked from prior drawdown-aware tech sweep.
BASE_TECH_WEIGHT = 0.80
HARD_MAX_DD = 0.35  # retail survival line — reject worse
TOP_N_SHOW = 4


def _curve(rets: pd.Series) -> list[dict]:
    eq = equity_from_returns(rets)
    return [
        {"date": dt.strftime("%Y-%m-%d"), "equity": round(float(val), 6)}
        for dt, val in eq.items()
    ]


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

    base_rets, base_stats = residual_momentum_returns(prices, **base_params)
    # Freeze a pre-confluence equity fingerprint so confidence annotations never drift curves.
    base_curve_fingerprint = [
        round(float(v), 8) for v in equity_from_returns(base_rets).iloc[::21].tolist()[:40]
    ]
    base_metrics = summarize(base_rets, "Base Resid Mom Tech 80%")
    base_score = survival_score(base_metrics, hard_max_dd=HARD_MAX_DD)
    trade_log = list(base_stats.get("trade_log") or [])
    conf_summary = dict(base_stats.get("confidence") or {})
    print(
        f"BASE: score={base_score:.3f} Sharpe={base_metrics['sharpe']:.2f} "
        f"CAGR={base_metrics['cagr']:.2%} MaxDD={base_metrics['max_dd']:.2%}"
    )
    if conf_summary:
        print(
            f"TRADE CONFIDENCE (background): mean={conf_summary.get('mean')} "
            f"median={conf_summary.get('median')} buckets={conf_summary.get('buckets')}"
        )

    rows: list[dict] = []
    curves: dict[str, list[dict]] = {}
    rets_map: dict[str, pd.Series] = {"base": base_rets}

    # Include naked base as candidate 0
    rows.append(
        {
            "id": "base",
            "label": "Base Tech 80% (no confluence)",
            "thesis": "Residual momentum with 80% tech long sleeve; no overlay.",
            "score": round(base_score, 6),
            "survived": base_score > -500,
            "metrics": base_metrics,
            "curve_key": "conf_base",
        }
    )
    curves["conf_base"] = _curve(base_rets)

    for conf in CONFLUENCES:
        rets = apply_confluence(conf.id, base_rets, prices)
        metrics = summarize(rets, conf.name)
        score = survival_score(metrics, hard_max_dd=HARD_MAX_DD)
        key = f"conf_{conf.id}"
        row = {
            "id": conf.id,
            "label": conf.name,
            "thesis": conf.thesis,
            "score": round(score, 6),
            "survived": score > -500,
            "metrics": metrics,
            "curve_key": key,
        }
        rows.append(row)
        curves[key] = _curve(rets)
        rets_map[conf.id] = rets
        flag = "OK" if row["survived"] else "REJECT"
        print(
            f"{flag} {conf.id}: score={score:.3f} Sharpe={metrics['sharpe']:.2f} "
            f"CAGR={metrics['cagr']:.2%} MaxDD={metrics['max_dd']:.2%}"
        )

    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i

    survivors = [r for r in ranked if r["survived"]]
    top = (survivors or ranked)[:TOP_N_SHOW]
    best = top[0]
    a_rets = rets_map["base" if best["id"] == "base" else best["id"]]

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

    CONF_OUT.write_text(
        json.dumps(
            {
                "hard_max_dd": HARD_MAX_DD,
                "base_tech_weight": BASE_TECH_WEIGHT,
                "ranked": [
                    {
                        "rank": r["rank"],
                        "id": r["id"],
                        "label": r["label"],
                        "score": r["score"],
                        "survived": r["survived"],
                        "max_dd": r["metrics"]["max_dd"],
                        "sharpe": r["metrics"]["sharpe"],
                        "cagr": r["metrics"]["cagr"],
                    }
                    for r in ranked
                ],
                "top": top_payload,
            },
            indent=2,
        )
    )

    # Guardrail: confidence metadata must not mutate strategy returns.
    post_fingerprint = [
        round(float(v), 8) for v in equity_from_returns(base_rets).iloc[::21].tolist()[:40]
    ]
    if post_fingerprint != base_curve_fingerprint:
        raise RuntimeError("Confidence annotation unexpectedly changed base equity curve")

    recent_trades = trade_log[-60:]
    (ROOT / "outputs" / "trade_confidence.json").write_text(
        json.dumps(
            {
                "summary": conf_summary,
                "n_trades": len(trade_log),
                "trades": trade_log,
            },
            indent=2,
        )
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
                "candidates_including_base": len(rows),
                "survivors": len(survivors),
                "trade_confidence_note": (
                    "Per-trade confidence is background metadata only; "
                    "it does not change which trades are taken or equity curves."
                ),
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
            # Always include the established original residual-momentum book on charts.
            "conf_base": curves["conf_base"],
            **{r["curve_key"]: curves[r["curve_key"]] for r in top if r["curve_key"] != "conf_base"},
        },
        "confluence_bakeoff": {
            "hard_max_dd": HARD_MAX_DD,
            "catalog": catalog_meta(),
            "survivors": len(survivors),
            "tested": len(rows),
            "top": top_payload,
        },
        "trade_confidence": {
            "summary": conf_summary,
            "n_trades": len(trade_log),
            "recent_trades": recent_trades,
        },
        "lsc_event_count": int(len(events)),
        "warnings": [
            f"Base book = residual momentum @ {int(BASE_TECH_WEIGHT*100)}% tech (long-only).",
            f"Tested {len(CONFLUENCES)} confluence overlays + base; survivors keep |MaxDD| ≤ {int(HARD_MAX_DD*100)}%.",
            "Only the top surviving confluence strategies are charted (account-survival ranking).",
            "Trade confidence scores are diagnostic metadata only — they do not alter trades or charts.",
            "Strategy B is a daily sweep/reclaim proxy — not the full 5m ICT confluence engine yet.",
            "Interim decision only — not live capital advice. Past DD ≠ future DD.",
            f"Selected Strat A: {best['label']} (score={best['score']:.3f}, MaxDD={best['metrics']['max_dd']:.1%}).",
        ],
    }

    out = SITE_DATA / "bakeoff.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"Decision (interim): {decision}")
    print(f"Survivors: {len(survivors)}/{len(rows)} (hard MaxDD ≤ {HARD_MAX_DD:.0%})")
    print("Top shown:")
    for r in top:
        m = r["metrics"]
        print(
            f"  #{r['rank']} {r['label']}: score={r['score']:.3f} "
            f"Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    for m in metrics:
        print(
            f"{m['name']}: Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    return payload


if __name__ == "__main__":
    run()
