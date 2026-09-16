"""Point-in-time transforms. No future bars enter a timestamp t value."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _s(x: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(x, pd.DataFrame):
        if "close" in x.columns:
            return x["close"]
        return x.iloc[:, 0]
    return x.astype(float)


def returns(close: pd.Series, period: int = 1) -> pd.Series:
    """Simple return over `period` bars. Horizon = period days. Unit: fraction."""
    return _s(close).pct_change(period)


def momentum(close: pd.Series, period: int) -> pd.Series:
    """Close / close.shift(period) - 1. Same as returns(period)."""
    return returns(close, period)


def residual_momentum(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    """Fast momentum minus slow momentum (residual / relative momentum)."""
    return momentum(close, fast) - momentum(close, slow)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder-style RSI in 0–100. Uses ewm(alpha=1/period) on past deltas only."""
    c = _s(close)
    delta = c.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    return out


def volume_zscore(volume: pd.Series, window: int = 20) -> pd.Series:
    v = volume.astype(float)
    mu = v.rolling(window, min_periods=max(5, window // 4)).mean()
    sd = v.rolling(window, min_periods=max(5, window // 4)).std(ddof=0)
    return (v - mu) / sd.replace(0.0, np.nan)


def dollar_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
    return _s(close) * volume.astype(float)


def volume_price_trend(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Cumulative VPT: sum(volume * close.pct_change())."""
    ret = _s(close).pct_change()
    return (volume.astype(float) * ret.fillna(0.0)).cumsum()


def close_to_close_vol(close: pd.Series, window: int) -> pd.Series:
    """Realized vol: std of 1d log returns * sqrt(365). Unit: annualized fraction."""
    log_ret = np.log(_s(close) / _s(close).shift(1))
    return log_ret.rolling(window, min_periods=max(5, window // 4)).std(ddof=0) * np.sqrt(365.0)


def parkinson_vol(high: pd.Series, low: pd.Series, window: int) -> pd.Series:
    """Parkinson range vol, annualized. Uses high/low through t only."""
    rs = np.log(high.astype(float) / low.astype(float).replace(0.0, np.nan)) ** 2
    const = 1.0 / (4.0 * np.log(2.0))
    return (rs.rolling(window, min_periods=max(5, window // 4)).mean() * const * 365.0) ** 0.5


def vol_of_vol(close: pd.Series, vol_window: int = 20, of_window: int = 20) -> pd.Series:
    rv = close_to_close_vol(close, vol_window)
    return rv.rolling(of_window, min_periods=max(5, of_window // 4)).std(ddof=0)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    h, l, c = high.astype(float), low.astype(float), _s(close)
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()


def range_pct(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    return (high.astype(float) - low.astype(float)) / _s(close).replace(0.0, np.nan)


def ma_distance(close: pd.Series, window: int) -> pd.Series:
    """close / SMA(window) - 1. Unit: fraction. Horizon = window."""
    c = _s(close)
    ma = c.rolling(window, min_periods=window).mean()
    return c / ma.replace(0.0, np.nan) - 1.0


def breakout(close: pd.Series, window: int = 20) -> pd.Series:
    """+1 if close == rolling max, -1 if == rolling min, else 0. Inclusive of t."""
    c = _s(close)
    hi = c.rolling(window, min_periods=window).max()
    lo = c.rolling(window, min_periods=window).min()
    out = pd.Series(0.0, index=c.index)
    out = out.mask(c >= hi, 1.0)
    out = out.mask(c <= lo, -1.0)
    return out


def liquidity_proxy(volume: pd.Series, atr_series: pd.Series) -> pd.Series:
    """volume / ATR. Higher = more activity per unit range."""
    return volume.astype(float) / atr_series.replace(0.0, np.nan)


def rolling_corr(a: pd.Series, b: pd.Series, window: int) -> pd.Series:
    """Rolling correlation of two aligned series (typically returns)."""
    return a.rolling(window, min_periods=max(10, window // 3)).corr(b)


def change(series: pd.Series, period: int = 1) -> pd.Series:
    return series.astype(float).diff(period)
