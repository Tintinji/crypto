"""OHLCV price/volume factors for BTC, ETH, SOL (and any listed crypto)."""

from __future__ import annotations

import pandas as pd

from factorlib.factors.math import (
    atr,
    breakout,
    close_to_close_vol,
    dollar_volume,
    liquidity_proxy,
    ma_distance,
    momentum,
    parkinson_vol,
    range_pct,
    residual_momentum,
    returns,
    rsi,
    vol_of_vol,
    volume_price_trend,
    volume_zscore,
)
from factorlib.registry import FactorSpec, register

_ASSETS = ("btc", "eth", "sol")
_TICKER = {"btc": "BTC-USD", "eth": "ETH-USD", "sol": "SOL-USD"}


def _prefix(asset: str, name: str) -> str:
    return f"px_{asset}_{name}"


def register_pv_specs() -> None:
    from factorlib.registry import all_specs

    if any(s.id.startswith("px_btc_mom_") for s in all_specs().values()):
        return
    specs: list[FactorSpec] = []
    for asset, ticker in _TICKER.items():
        specs.extend(
            [
                FactorSpec(_prefix(asset, "ret_1d"), f"{ticker} 1d return", "fraction", "1d", "pricevolume", "returns"),
                FactorSpec(_prefix(asset, "mom_5"), f"{ticker} 5d momentum", "fraction", "5d", "pricevolume", "momentum"),
                FactorSpec(_prefix(asset, "mom_20"), f"{ticker} 20d momentum", "fraction", "20d", "pricevolume", "momentum"),
                FactorSpec(_prefix(asset, "mom_60"), f"{ticker} 60d momentum", "fraction", "20d", "pricevolume", "momentum"),
                FactorSpec(_prefix(asset, "resid_mom"), f"{ticker} 5d minus 20d momentum", "fraction", "5d", "pricevolume", "residual momentum"),
                FactorSpec(_prefix(asset, "rsi_14"), f"{ticker} 14d Wilder RSI", "0-100", "1d", "pricevolume", "RSI"),
                FactorSpec(_prefix(asset, "vol_z_20"), f"{ticker} 20d volume z-score", "z", "1d", "pricevolume", "volume"),
                FactorSpec(_prefix(asset, "dollar_vol"), f"{ticker} close * volume", "USD", "1d", "pricevolume", "dollar volume"),
                FactorSpec(_prefix(asset, "vpt"), f"{ticker} cumulative volume-price trend", "shares", "1d", "pricevolume", "VPT"),
                FactorSpec(_prefix(asset, "rv_cc_20"), f"{ticker} 20d close-to-close vol (ann.)", "ann. fraction", "20d", "pricevolume", "volatility"),
                FactorSpec(_prefix(asset, "rv_pk_20"), f"{ticker} 20d Parkinson vol (ann.)", "ann. fraction", "20d", "pricevolume", "Parkinson vol"),
                FactorSpec(_prefix(asset, "vov_20"), f"{ticker} vol-of-vol of 20d RV", "ann. fraction", "20d", "pricevolume", "vol-of-vol"),
                FactorSpec(_prefix(asset, "atr_14"), f"{ticker} 14d ATR (price units)", "price", "1d", "pricevolume", "ATR"),
                FactorSpec(_prefix(asset, "range_pct"), f"{ticker} high-low / close", "fraction", "1d", "pricevolume", "range"),
                FactorSpec(_prefix(asset, "breakout_20"), f"{ticker} 20d high/low breakout (-1/0/1)", "flag", "20d", "pricevolume", "breakout vs MA/range"),
                FactorSpec(_prefix(asset, "dist_ma_20"), f"{ticker} distance to 20d SMA", "fraction", "20d", "pricevolume", "breakout vs MA"),
                FactorSpec(_prefix(asset, "liq_proxy"), f"{ticker} volume / ATR", "shares/price", "1d", "pricevolume", "liquidity proxy"),
            ]
        )
    for s in specs:
        register(s)


def _one_asset(df: pd.DataFrame, asset: str) -> pd.DataFrame:
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    atr14 = atr(h, l, c, 14)
    out = pd.DataFrame(
        {
            _prefix(asset, "ret_1d"): returns(c, 1),
            _prefix(asset, "mom_5"): momentum(c, 5),
            _prefix(asset, "mom_20"): momentum(c, 20),
            _prefix(asset, "mom_60"): momentum(c, 60),
            _prefix(asset, "resid_mom"): residual_momentum(c, 5, 20),
            _prefix(asset, "rsi_14"): rsi(c, 14),
            _prefix(asset, "vol_z_20"): volume_zscore(v, 20),
            _prefix(asset, "dollar_vol"): dollar_volume(c, v),
            _prefix(asset, "vpt"): volume_price_trend(c, v),
            _prefix(asset, "rv_cc_20"): close_to_close_vol(c, 20),
            _prefix(asset, "rv_pk_20"): parkinson_vol(h, l, 20),
            _prefix(asset, "vov_20"): vol_of_vol(c, 20, 20),
            _prefix(asset, "atr_14"): atr14,
            _prefix(asset, "range_pct"): range_pct(h, l, c),
            _prefix(asset, "breakout_20"): breakout(c, 20),
            _prefix(asset, "dist_ma_20"): ma_distance(c, 20),
            _prefix(asset, "liq_proxy"): liquidity_proxy(v, atr14),
        },
        index=df.index,
    )
    return out


def compute_pricevolume_factors(
    frames: dict[str, pd.DataFrame],
    tickers: list[str] | None = None,
) -> pd.DataFrame:
    register_pv_specs()
    wanted = tickers or list(_TICKER.values())
    rev = {v: k for k, v in _TICKER.items()}
    pieces: list[pd.DataFrame] = []
    for ticker in wanted:
        if ticker not in frames or frames[ticker] is None or frames[ticker].empty:
            continue
        asset = rev.get(ticker)
        if asset is None:
            # Allow extra alts: slug from ticker
            asset = ticker.split("-")[0].lower()
        df = frames[ticker].copy()
        df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
        df = df[~df.index.duplicated(keep="last")].sort_index()
        pieces.append(_one_asset(df, asset))
    if not pieces:
        return pd.DataFrame()
    panel = pieces[0]
    for extra in pieces[1:]:
        panel = panel.join(extra, how="outer")
    return panel.sort_index()
