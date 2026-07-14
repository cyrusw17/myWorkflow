from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data import fetch_ohlc, load_universe
from src.metrics import equity_from_returns, summarize, vol_target_returns
from src.strategies_a import TECH_TICKERS, residual_momentum_returns
from src.strategies_b import lsc_proxy_returns

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
EVENTS = ROOT / "outputs" / "lsc_events.csv"

# Broader liquid book so residual momentum can trade ~20×/month with a tech sleeve.
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

    a_params = {
        "lookback_beta": 90,
        "formation": 63,
        "skip": 1,
        "n_hold": 8,
        "rebalance_every": 1,
        "entries_per_rebalance": 1,
        "min_tech_share": 0.30,
        "cost_bps": 5.0,
    }
    a_rets, a_stats = residual_momentum_returns(prices, **a_params)
    b_rets, events = lsc_proxy_returns(spy_ohlc)
    events.to_csv(EVENTS, index=False)

    # Align
    idx = spy_rets.index.intersection(a_rets.index).intersection(b_rets.index)
    spy_rets = spy_rets.loc[idx]
    a_rets = a_rets.loc[idx]
    b_rets = b_rets.loc[idx]

    # Vol-match SPY to Strategy A realized vol
    a_vol = float(a_rets.std() * (252 ** 0.5))
    spy_vm = vol_target_returns(spy_rets, target_vol=max(a_vol, 0.05))

    metrics = [
        summarize(spy_rets, "SPY B&H"),
        summarize(spy_vm, "SPY vol-match"),
        summarize(a_rets, "Strat A Residual Momentum"),
        summarize(b_rets, "Strat B LSC proxy"),
    ]

    # Naive interim decision (will be replaced by walk-forward memo)
    sharpes = {m["name"]: m["sharpe"] for m in metrics}
    eligible = []
    if sharpes["Strat A Residual Momentum"] > sharpes["SPY vol-match"]:
        eligible.append("A")
    if sharpes["Strat B LSC proxy"] > sharpes["SPY B&H"] and metrics[3]["sharpe"] > 0:
        eligible.append("B")
    if eligible == ["A"]:
        decision = "SHIP_A_PAPER"
    elif eligible == ["B"]:
        decision = "SHIP_B_PAPER"
    elif set(eligible) == {"A", "B"}:
        decision = "SHIP_ENSEMBLE_PAPER"
    else:
        decision = "KILL_REDESIGN"

    tech_ok = a_stats["tech_trade_share"] >= a_params["min_tech_share"] - 1e-9
    trade_rate = a_stats["trades_per_month"]
    trade_rate_ok = 15.0 <= trade_rate <= 28.0  # aim ~20, allow band

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "yahoo finance chart API (daily OHLC, cached)",
        "universe": UNIVERSE,
        "assumptions": {
            "start": "2018-01-01",
            "cost_bps_per_turnover_or_entry": 5.0,
            "strategy_a": {
                **{k: v for k, v in a_params.items() if k != "cost_bps"},
                "tech_tickers": sorted(t for t in TECH_TICKERS if t in UNIVERSE),
                "target_tech_trade_share": a_params["min_tech_share"],
                "target_trades_per_month": 20,
                "realized_tech_trade_share": round(a_stats["tech_trade_share"], 4),
                "realized_trades_per_month": round(a_stats["trades_per_month"], 2),
                "n_trades": a_stats["n_trades"],
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
        },
        "lsc_event_count": int(len(events)),
        "strategy_a_ops": a_stats,
        "warnings": [
            "Strategy B is a daily sweep/reclaim proxy — not the full 5m ICT confluence engine yet.",
            "This decision_status is interim (no nested walk-forward). Treat as research, not capital deployment.",
            (
                f"Strat A tech trade share {a_stats['tech_trade_share']:.1%} "
                f"({'OK' if tech_ok else 'BELOW'} ≥{a_params['min_tech_share']:.0%} target)."
            ),
            (
                f"Strat A trades/month {a_stats['trades_per_month']:.1f} "
                f"({'OK' if trade_rate_ok else 'OFF'} ~20 target band 15–28)."
            ),
        ],
    }

    out = SITE_DATA / "bakeoff.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"Decision (interim): {decision}")
    print(
        f"Strat A ops: trades/mo={a_stats['trades_per_month']:.1f} "
        f"tech_share={a_stats['tech_trade_share']:.1%} n_trades={a_stats['n_trades']}"
    )
    for m in metrics:
        print(
            f"{m['name']}: Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    return payload


if __name__ == "__main__":
    run()
