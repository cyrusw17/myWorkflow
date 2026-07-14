from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data import fetch_ohlc, load_universe
from src.metrics import equity_from_returns, summarize, vol_target_returns
from src.strategies_a import residual_momentum_returns
from src.strategies_b import lsc_proxy_returns

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
EVENTS = ROOT / "outputs" / "lsc_events.csv"

UNIVERSE = [
    "SPY",
    "QQQ",
    "IWM",
    "XLK",
    "XLF",
    "XLE",
    "XLV",
    "XLI",
    "XLY",
    "XLP",
    "XLU",
    "GLD",
    "TLT",
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

    a_rets = residual_momentum_returns(prices)
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

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "yahoo finance chart API (daily OHLC, cached)",
        "universe": UNIVERSE,
        "assumptions": {
            "start": "2018-01-01",
            "cost_bps_per_turnover_or_entry": 5.0,
            "strategy_a": {
                "lookback_beta": 90,
                "formation": 63,
                "skip": 1,
                "top_quantile": 0.2,
                "rebalance_every": 5,
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
        "warnings": [
            "Strategy B is a daily sweep/reclaim proxy — not the full 5m ICT confluence engine yet.",
            "This decision_status is interim (no nested walk-forward). Treat as research, not capital deployment.",
        ],
    }

    out = SITE_DATA / "bakeoff.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"Decision (interim): {decision}")
    for m in metrics:
        print(
            f"{m['name']}: Sharpe={m['sharpe']:.2f} CAGR={m['cagr']:.2%} MaxDD={m['max_dd']:.2%}"
        )
    return payload


if __name__ == "__main__":
    run()
