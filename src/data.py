from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
UA = "Mozilla/5.0 (compatible; ai-agent-bakeoff/0.1; +https://github.com/cyrusw17/myWorkflow)"


def cache_key(ticker: str) -> str:
    """Filesystem-safe cache stem for Yahoo symbols like EURUSD=X / BTC-USD / ^GSPC."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", ticker.upper())


def fetch_ohlc(ticker: str, start: str = "2018-01-01", *, refresh: bool = False) -> pd.DataFrame:
    """Daily OHLC from Yahoo chart API with local CSV cache."""
    cache_path = CACHE / f"{cache_key(ticker)}_ohlc.csv"
    start_ts = pd.Timestamp(start)

    if cache_path.exists() and not refresh:
        df = pd.read_csv(cache_path, parse_dates=["Date"])
    else:
        params = {
            "interval": "1d",
            "period1": int(start_ts.timestamp()),
            "period2": int(pd.Timestamp.utcnow().timestamp()),
            "events": "history",
        }
        r = requests.get(
            YAHOO.format(symbol=ticker),
            params=params,
            timeout=30,
            headers={"User-Agent": UA},
        )
        r.raise_for_status()
        payload = r.json()
        result = (payload.get("chart") or {}).get("result") or []
        if not result:
            raise RuntimeError(f"No Yahoo chart result for {ticker}: {json.dumps(payload)[:200]}")
        block = result[0]
        ts = block.get("timestamp") or []
        quote = (block.get("indicators") or {}).get("quote") or [{}]
        q = quote[0]
        if not ts:
            raise RuntimeError(f"Empty Yahoo series for {ticker}")
        df = pd.DataFrame(
            {
                "Date": pd.to_datetime(ts, unit="s").tz_localize("UTC").tz_convert(None).normalize(),
                "Open": q.get("open"),
                "High": q.get("high"),
                "Low": q.get("low"),
                "Close": q.get("close"),
            }
        ).dropna(subset=["Close"])
        df.to_csv(cache_path, index=False)

    df = df.sort_values("Date").set_index("Date")
    df = df[df.index >= start_ts]
    if df.empty:
        raise RuntimeError(f"No rows for {ticker} after {start}")
    return df.astype(float)


def fetch_daily(ticker: str, start: str = "2018-01-01", *, refresh: bool = False) -> pd.Series:
    close = fetch_ohlc(ticker, start=start, refresh=refresh)["Close"]
    close.name = ticker.upper()
    return close


def load_universe(
    tickers: list[str],
    start: str = "2018-01-01",
    *,
    refresh: bool = False,
    ffill_limit: int = 3,
) -> pd.DataFrame:
    series = []
    failed: list[str] = []
    for t in tickers:
        try:
            series.append(fetch_daily(t, start=start, refresh=refresh))
        except Exception as exc:  # noqa: BLE001 — skip thin / broken Yahoo symbols
            failed.append(f"{t} ({exc})")
    if not series:
        raise RuntimeError(f"No tickers loaded. Failures: {failed[:5]}")
    if failed:
        print(f"  skipped {len(failed)} ticker(s): {', '.join(x.split(' (')[0] for x in failed[:8])}"
              + ("…" if len(failed) > 8 else ""))
    prices = pd.concat(series, axis=1).sort_index()
    prices = prices.ffill(limit=ffill_limit).dropna(how="any")
    return prices
