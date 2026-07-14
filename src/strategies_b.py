from __future__ import annotations

import numpy as np
import pandas as pd


def lsc_proxy_returns(
    ohlc: pd.DataFrame,
    lookback_pool: int = 20,
    hold_days: int = 5,
    cost_bps: float = 5.0,
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Daily proxy for Liquidity Sweep Continuation on SPY until full 5m/1H stack exists.

    Uses OHLC:
    - Sweep of prior N-day high/low via intraday High/Low
    - Reclaim confirmation via Close back inside the pool
    - Hold continuation for `hold_days`
    """
    high = ohlc["High"].astype(float)
    low = ohlc["Low"].astype(float)
    close = ohlc["Close"].astype(float)
    pool_high = high.rolling(lookback_pool).max().shift(1)
    pool_low = low.rolling(lookback_pool).min().shift(1)
    rets = close.pct_change().fillna(0.0)

    events: list[dict] = []
    position = 0
    hold_left = 0
    strat = pd.Series(0.0, index=close.index, name="lsc_proxy")
    cost = cost_bps / 10000.0

    for i, dt in enumerate(close.index):
        if i < lookback_pool + 2:
            continue

        if hold_left > 0:
            strat.iloc[i] = position * float(rets.iloc[i])
            hold_left -= 1
            if hold_left == 0:
                events.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "state": "FLAT",
                        "side": position,
                        "reason": "hold_expired",
                        "price": float(close.iloc[i]),
                    }
                )
                position = 0
            continue

        ph = float(pool_high.iloc[i]) if np.isfinite(pool_high.iloc[i]) else np.nan
        pl = float(pool_low.iloc[i]) if np.isfinite(pool_low.iloc[i]) else np.nan
        hi = float(high.iloc[i])
        lo = float(low.iloc[i])
        cl = float(close.iloc[i])

        # Bullish: sweep prior low, close back above it
        bull = np.isfinite(pl) and lo < pl and cl > pl
        # Bearish: sweep prior high, close back below it
        bear = np.isfinite(ph) and hi > ph and cl < ph

        if bull and not bear:
            position = 1
            hold_left = hold_days
            strat.iloc[i] = position * float(rets.iloc[i]) - cost
            events.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "state": "ARMED",
                    "side": 1,
                    "reason": "bull_sweep_reclaim",
                    "price": cl,
                    "pool": pl,
                }
            )
        elif bear and not bull:
            position = -1
            hold_left = hold_days
            strat.iloc[i] = position * float(rets.iloc[i]) - cost
            events.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "state": "ARMED",
                    "side": -1,
                    "reason": "bear_sweep_reclaim",
                    "price": cl,
                    "pool": ph,
                }
            )

    return strat.fillna(0.0), pd.DataFrame(events)
