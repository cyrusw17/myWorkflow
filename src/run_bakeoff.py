from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data import fetch_ohlc, load_universe
from src.metrics import equity_from_returns, summarize, vol_target_returns
from src.strategies_a import TECH_TICKERS, drawdown_aware_score, residual_momentum_returns
from src.strategies_b import lsc_proxy_returns

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
EVENTS = ROOT / "outputs" / "lsc_events.csv"
SWEEP_OUT = ROOT / "outputs" / "tech_weight_sweep.json"

UNIVERSE = [
    "SPY",
    # Technology
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
    # Non-tech diversifiers
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

# Dense sweep 25% → 95% inclusive.
TECH_WEIGHTS = [round(x / 100.0, 2) for x in range(25, 100, 5)]  # 25,30,...,95


def _curve(rets: pd.Series) -> list[dict]:
    eq = equity_from_returns(rets)
    out = []
    for dt, val in eq.items():
        out.append({"date": dt.strftime("%Y-%m-%d"), "equity": round(float(val), 6)})
    return out


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
    }

    sweep_rows: list[dict] = []
    curves_by_weight: dict[str, list[dict]] = {}
    rets_by_weight: dict[float, pd.Series] = {}

    for w in TECH_WEIGHTS:
        a_rets, a_stats = residual_momentum_returns(prices, tech_weight=w, **base_params)
        label = f"Tech {int(round(w * 100))}%"
        metrics = summarize(a_rets, label)
        score = drawdown_aware_score(metrics)
        key = f"tech_{int(round(w * 100)):02d}"
        row = {
            "tech_weight": w,
            "label": label,
            "curve_key": key,
            "score": round(score, 6),
            "metrics": metrics,
            "ops": {
                "trades_per_month": round(a_stats["trades_per_month"], 2),
                "tech_trade_share": round(a_stats["tech_trade_share"], 4),
                "n_trades": a_stats["n_trades"],
            },
        }
        sweep_rows.append(row)
        curves_by_weight[key] = _curve(a_rets)
        rets_by_weight[w] = a_rets
        print(
            f"{label}: score={score:.3f} Sharpe={metrics['sharpe']:.2f} "
            f"CAGR={metrics['cagr']:.2%} MaxDD={metrics['max_dd']:.2%} Calmar={metrics['calmar']:.2f}"
        )

    # Rank by drawdown-aware score; top 5 for the comparison chart.
    ranked = sorted(sweep_rows, key=lambda r: r["score"], reverse=True)
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i
    top5 = ranked[:5]
    best = top5[0]
    best_w = best["tech_weight"]
    a_rets = rets_by_weight[best_w]

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
        summarize(a_rets, f"Strat A Resid Mom ({best['label']})"),
        summarize(b_rets, "Strat B LSC proxy"),
    ]

    sharpes = {m["name"]: m["sharpe"] for m in metrics}
    eligible = []
    if metrics[2]["sharpe"] > metrics[1]["sharpe"]:
        eligible.append("A")
    if metrics[3]["sharpe"] > metrics[0]["sharpe"] and metrics[3]["sharpe"] > 0:
        eligible.append("B")
    if eligible == ["A"]:
        decision = "SHIP_A_PAPER"
    elif eligible == ["B"]:
        decision = "SHIP_B_PAPER"
    elif set(eligible) == {"A", "B"}:
        decision = "SHIP_ENSEMBLE_PAPER"
    else:
        decision = "KILL_REDESIGN"

    top5_payload = []
    for row in top5:
        top5_payload.append(
            {
                "rank": row["rank"],
                "label": row["label"],
                "tech_weight": row["tech_weight"],
                "score": row["score"],
                "curve_key": row["curve_key"],
                "cagr": row["metrics"]["cagr"],
                "sharpe": row["metrics"]["sharpe"],
                "max_dd": row["metrics"]["max_dd"],
                "calmar": row["metrics"]["calmar"],
            }
        )

    SWEEP_OUT.write_text(json.dumps({"ranked": ranked, "top5": top5_payload}, indent=2, default=str))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "yahoo finance chart API (daily OHLC, cached)",
        "universe": UNIVERSE,
        "assumptions": {
            "start": "2018-01-01",
            "cost_bps_per_turnover_or_entry": 5.0,
            "strategy_a": {
                "mode": "tech_weight_residual_momentum",
                **{k: v for k, v in base_params.items() if k != "cost_bps"},
                "tech_weight": best_w,
                "tech_tickers": sorted(t for t in TECH_TICKERS if t in UNIVERSE),
                "sweep_weights": TECH_WEIGHTS,
                "score_method": "0.55*Calmar + 0.45*Sharpe, soft DD penalty if |maxDD|>25%",
                "selected_from_sweep": best["label"],
                "selected_score": best["score"],
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
            **{row["curve_key"]: curves_by_weight[row["curve_key"]] for row in top5},
        },
        "tech_sweep": {
            "weights_tested": TECH_WEIGHTS,
            "score_method": "0.55*Calmar + 0.45*Sharpe with soft max-DD penalty",
            "ranked": [
                {
                    "rank": r["rank"],
                    "label": r["label"],
                    "tech_weight": r["tech_weight"],
                    "score": r["score"],
                    "cagr": r["metrics"]["cagr"],
                    "sharpe": r["metrics"]["sharpe"],
                    "max_dd": r["metrics"]["max_dd"],
                    "calmar": r["metrics"]["calmar"],
                    "curve_key": r["curve_key"] if r["rank"] <= 5 else None,
                }
                for r in ranked
            ],
            "top5": top5_payload,
        },
        "lsc_event_count": int(len(events)),
        "warnings": [
            "Strat A is residual momentum with a fixed tech portfolio weight (swept 25–95%).",
            "Winner selected by drawdown-aware score: 0.55*Calmar + 0.45*Sharpe (soft penalty if |maxDD|>25%).",
            "Strategy B is a daily sweep/reclaim proxy — not the full 5m ICT confluence engine yet.",
            "This decision_status is interim (no nested walk-forward). Treat as research, not capital deployment.",
            f"Selected Strat A tech weight: {best['label']} (score={best['score']:.3f}).",
            "Top 5 tech-weight variants are plotted on the dedicated comparison chart.",
        ],
    }

    out = SITE_DATA / "bakeoff.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"Decision (interim): {decision}")
    print(f"Selected: {best['label']} score={best['score']:.3f}")
    print("Top 5:")
    for row in top5:
        m = row["metrics"]
        print(
            f"  #{row['rank']} {row['label']}: score={row['score']:.3f} "
            f"Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    for m in metrics:
        print(
            f"{m['name']}: Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    return payload


if __name__ == "__main__":
    run()
