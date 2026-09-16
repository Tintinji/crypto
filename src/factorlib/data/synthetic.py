"""Deterministic offline OHLCV so paper/ingest works without Yahoo."""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from factorlib.data.store import write_ohlcv

# Seed prices roughly in 2023-ish neighborhoods (research fixtures, not quotes).
_STARTS: dict[str, float] = {
    "BTC-USD": 23000.0,
    "ETH-USD": 1600.0,
    "SOL-USD": 22.0,
    "^TNX": 38.5,  # CBOE *10 convention
    "2YY=F": 42.0,
    "^IRX": 47.0,
    "DX-Y.NYB": 103.0,
    "USDJPY=X": 132.0,
    "CL=F": 78.0,
    "BZ=F": 82.0,
    "GC=F": 1900.0,
    "^GSPC": 3900.0,
    "^NDX": 12000.0,
    "KRW=X": 1300.0,
    "BTC-KRW": 23000.0 * 1300.0,
}


def _rng(ticker: str) -> np.random.Generator:
    digest = hashlib.sha256(ticker.encode()).digest()
    seed = int.from_bytes(digest[:8], "little") % (2**32)
    return np.random.default_rng(seed)


def make_ohlcv(
    ticker: str,
    start: str = "2023-01-01",
    end: str = "2026-09-16",
    start_price: float | None = None,
) -> pd.DataFrame:
    idx = pd.bdate_range(start, end, freq="C")
    rng = _rng(ticker)
    n = len(idx)
    px0 = start_price if start_price is not None else _STARTS.get(ticker, 100.0)
    # Mild drift + vol; crypto gets fatter tails.
    is_crypto = ticker.endswith("-USD") or ticker.endswith("-KRW")
    vol = 0.028 if is_crypto else 0.009
    rets = rng.normal(0.0004 if is_crypto else 0.00015, vol, size=n)
    close = px0 * np.exp(np.cumsum(rets))
    close = np.maximum(close, 1e-6)
    high = close * (1 + rng.uniform(0.001, 0.02 if is_crypto else 0.008, n))
    low = close * (1 - rng.uniform(0.001, 0.02 if is_crypto else 0.008, n))
    open_ = np.concatenate([[close[0]], close[:-1]])
    volume = rng.uniform(5e8, 3e10, n) if is_crypto else rng.uniform(1e6, 8e7, n)
    df = pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(high, np.maximum(open_, close)),
            "low": np.minimum(low, np.minimum(open_, close)),
            "close": close,
            "volume": volume,
        },
        index=idx,
    )
    df.index.name = "date"
    return df


def seed_offline_universe(tickers: list[str], persist: bool = True) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for t in tickers:
        df = make_ohlcv(t)
        out[t] = df
        if persist:
            write_ohlcv(t, df)
    return out
