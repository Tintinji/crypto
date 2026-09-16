"""yfinance download wrapper. All network calls are try/except'd."""

from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd

from factorlib.data.store import write_ohlcv

logger = logging.getLogger(__name__)

OHLCV_COLS = ["open", "high", "low", "close", "volume"]


def _flatten_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=OHLCV_COLS)
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        # yfinance multi-ticker or (Price, Ticker) layout
        level0 = [str(c[0]).lower() for c in out.columns]
        if set(level0) & {"open", "high", "low", "close", "adj close", "volume"}:
            out.columns = level0
        else:
            out.columns = [str(c[-1]).lower() for c in out.columns]
    else:
        out.columns = [str(c).lower() for c in out.columns]
    rename = {"adj close": "close", "adj_close": "close"}
    out = out.rename(columns=rename)
    keep = [c for c in OHLCV_COLS if c in out.columns]
    out = out[keep]
    for c in OHLCV_COLS:
        if c not in out.columns:
            out[c] = 0.0 if c == "volume" else pd.NA
    out = out[OHLCV_COLS]
    out.index = pd.DatetimeIndex(out.index).tz_localize(None)
    out = out[~out.index.duplicated(keep="last")].sort_index()
    out = out.dropna(subset=["close"])
    return out


def normalize_yield(series: pd.Series) -> pd.Series:
    """CBOE ^TNX/^IRX are often yield*10. If median > 20, divide by 10."""
    s = pd.to_numeric(series, errors="coerce")
    med = s.dropna().median()
    if pd.notna(med) and med > 20:
        return s / 10.0
    return s


def download_ohlcv(
    ticker: str,
    start: str | None = "2023-01-01",
    end: str | None = None,
) -> pd.DataFrame | None:
    """Download one ticker. Returns None on any failure (never raises)."""
    try:
        import yfinance as yf

        df = yf.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
        out = _flatten_ohlcv(df)
        if out.empty:
            logger.warning("yfinance returned empty frame for %s", ticker)
            return None
        return out
    except Exception as exc:  # noqa: BLE001 — network/API must never crash pipeline
        logger.warning("yfinance download failed for %s: %s", ticker, exc)
        return None


def download_many(
    tickers: Iterable[str],
    start: str | None = "2023-01-01",
    end: str | None = None,
    persist: bool = True,
) -> dict[str, pd.DataFrame]:
    got: dict[str, pd.DataFrame] = {}
    for t in tickers:
        df = download_ohlcv(t, start=start, end=end)
        if df is None or df.empty:
            continue
        got[t] = df
        if persist:
            write_ohlcv(t, df)
    return got
