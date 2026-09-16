"""Every timestamp t may only depend on bars ≤ t."""

from __future__ import annotations

import numpy as np
import pandas as pd

from factorlib.data.synthetic import make_ohlcv
from factorlib.factors.math import (
    atr,
    breakout,
    close_to_close_vol,
    ma_distance,
    momentum,
    parkinson_vol,
    rsi,
    volume_zscore,
)
from factorlib.pricevolume.compute import compute_pricevolume_factors


def _ohlcv(n: int = 80) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2024-01-01", periods=n)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    high = close * 1.01
    low = close * 0.99
    open_ = np.r_[close[0], close[:-1]]
    vol = rng.uniform(1e6, 2e6, n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
        index=idx,
    )


def test_math_transforms_are_point_in_time():
    df = _ohlcv(90)
    full = {
        "mom20": momentum(df["close"], 20),
        "rsi": rsi(df["close"], 14),
        "vz": volume_zscore(df["volume"], 20),
        "rv": close_to_close_vol(df["close"], 30),
        "pk": parkinson_vol(df["high"], df["low"], 20),
        "atr": atr(df["high"], df["low"], df["close"], 14),
        "dist": ma_distance(df["close"], 20),
        "bo": breakout(df["close"], 20),
    }
    # Recompute on a prefix; last prefix value must match full[t]
    check_at = [25, 40, 70]
    for t in check_at:
        pref = df.iloc[: t + 1]
        pref_map = {
            "mom20": momentum(pref["close"], 20),
            "rsi": rsi(pref["close"], 14),
            "vz": volume_zscore(pref["volume"], 20),
            "rv": close_to_close_vol(pref["close"], 30),
            "pk": parkinson_vol(pref["high"], pref["low"], 20),
            "atr": atr(pref["high"], pref["low"], pref["close"], 14),
            "dist": ma_distance(pref["close"], 20),
            "bo": breakout(pref["close"], 20),
        }
        for name, series in full.items():
            a = series.iloc[t]
            b = pref_map[name].iloc[-1]
            if pd.isna(a) and pd.isna(b):
                continue
            assert a == b or np.isclose(a, b, rtol=1e-12, atol=1e-12), f"{name} t={t}"


def test_panel_prefix_matches_full_at_t():
    btc = make_ohlcv("BTC-USD", start="2023-01-01", end="2024-06-01")
    eth = make_ohlcv("ETH-USD", start="2023-01-01", end="2024-06-01")
    sol = make_ohlcv("SOL-USD", start="2023-01-01", end="2024-06-01")
    frames = {"BTC-USD": btc, "ETH-USD": eth, "SOL-USD": sol}
    full = compute_pricevolume_factors(frames)
    cut = btc.index[120]
    pref = {k: v.loc[:cut] for k, v in frames.items()}
    partial = compute_pricevolume_factors(pref)
    cols = ["px_btc_mom_20", "px_btc_rsi_14", "px_btc_rv_cc_20", "px_eth_mom_5"]
    for c in cols:
        a = full.loc[cut, c]
        b = partial.loc[cut, c]
        if pd.isna(a) and pd.isna(b):
            continue
        assert np.isclose(float(a), float(b), rtol=1e-12, atol=1e-12), c


def test_future_shock_does_not_leak_backward():
    df = _ohlcv(50)
    base = momentum(df["close"], 5)
    shocked = df.copy()
    shocked.iloc[-1, shocked.columns.get_loc("close")] *= 3.0
    alt = momentum(shocked["close"], 5)
    # All bars except the last 5 (window that includes the shocked close) stay equal
    assert np.allclose(base.iloc[:-5].fillna(0), alt.iloc[:-5].fillna(0))
    assert not np.isclose(base.iloc[-1], alt.iloc[-1])
