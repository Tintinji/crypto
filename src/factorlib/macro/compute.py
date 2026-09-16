"""Macro / cross-asset / flow / calendar factor construction."""

from __future__ import annotations

import logging

import pandas as pd

from factorlib.data.calendar import event_flags, hormuz_flag, load_event_table, load_hormuz_table
from factorlib.data.etf_flows import align_etf_flows, load_etf_flows
from factorlib.data.yahoo import normalize_yield
from factorlib.factors.math import change, close_to_close_vol, ma_distance, returns, rolling_corr
from factorlib.registry import FactorSpec, register

logger = logging.getLogger(__name__)

FED_RESTRICTIVE_THRESHOLD = 4.0  # 10Y yield percent


def register_macro_specs() -> None:
    """Idempotent registration of macro factor metadata."""
    from factorlib.registry import all_specs

    if any(s.category in {"macro", "cross", "flow", "calendar"} for s in all_specs().values()):
        return
    specs = [
        FactorSpec("macro_us10y_level", "US 10Y yield level (^TNX, percent)", "percent", "1d", "macro", "Fed path / discount rate"),
        FactorSpec("macro_us10y_chg", "1d change in US 10Y yield", "pp", "1d", "macro", "Fed path"),
        FactorSpec("macro_us2y_level", "US 2Y yield proxy level", "percent", "1d", "macro", "Fed path / front-end"),
        FactorSpec("macro_us2y_chg", "1d change in US 2Y yield proxy", "pp", "1d", "macro", "Fed path"),
        FactorSpec("macro_us13w_level", "13-week T-bill yield (^IRX)", "percent", "1d", "macro", "fed-funds proxy"),
        FactorSpec("macro_fed_funds_proxy", "Alias of 13W T-bill as fed-funds proxy", "percent", "1d", "macro", "Fed path"),
        FactorSpec("macro_2s10s", "10Y minus 2Y yield curve slope", "pp", "1d", "macro", "curve / recession risk"),
        FactorSpec("macro_fed_restrictive_flag", f"1 if 10Y > {FED_RESTRICTIVE_THRESHOLD}%", "flag", "1d", "macro", "Fed restrictive stance"),
        FactorSpec("macro_dxy_level", "DXY spot level", "index", "1d", "macro", "DXY dollar cycle"),
        FactorSpec("macro_dxy_ret_20d", "DXY 20d simple return", "fraction", "20d", "macro", "DXY"),
        FactorSpec("macro_usdjpy_ret_20d", "USDJPY 20d simple return", "fraction", "20d", "macro", "USDJPY / carry"),
        FactorSpec("macro_wti_ret_20d", "WTI 20d return", "fraction", "20d", "macro", "oil / Hormuz"),
        FactorSpec("macro_brent_ret_20d", "Brent 20d return", "fraction", "20d", "macro", "oil / Hormuz"),
        FactorSpec("macro_oil_ret_20d", "Average of WTI/Brent 20d returns (available legs)", "fraction", "20d", "macro", "oil / Hormuz"),
        FactorSpec("macro_gold_ret_20d", "Gold 20d return", "fraction", "20d", "macro", "gold risk hedge"),
        FactorSpec("macro_spx_ret_20d", "S&P 500 20d return", "fraction", "20d", "macro", "risk-on equities"),
        FactorSpec("macro_ndx_ret_20d", "Nasdaq 100 20d return", "fraction", "20d", "macro", "risk-on / duration"),
        FactorSpec("px_btc_dist_200dma", "BTC close / 200d SMA - 1", "fraction", "20d", "crypto-macro", "cycle / 200d MA"),
        FactorSpec("px_btc_dist_365dma", "BTC close / 365d SMA - 1", "fraction", "20d", "crypto-macro", "cycle / 365d MA"),
        FactorSpec("px_eth_dist_200dma", "ETH close / 200d SMA - 1", "fraction", "20d", "crypto-macro", "ETH cycle"),
        FactorSpec("px_eth_dist_365dma", "ETH close / 365d SMA - 1", "fraction", "20d", "crypto-macro", "ETH cycle"),
        FactorSpec("px_btc_rv_30d", "BTC 30d close-to-close realized vol (ann.)", "ann. fraction", "20d", "crypto-macro", "realized vol"),
        FactorSpec("px_btc_rv_90d", "BTC 90d close-to-close realized vol (ann.)", "ann. fraction", "20d", "crypto-macro", "realized vol"),
        FactorSpec("px_eth_rv_30d", "ETH 30d realized vol (ann.)", "ann. fraction", "20d", "crypto-macro", "ETH vol"),
        FactorSpec("x_btc_spx_corr_20d", "20d corr BTC vs SPX daily returns", "corr", "20d", "cross", "BTC–SPX beta"),
        FactorSpec("x_btc_spx_corr_60d", "60d corr BTC vs SPX daily returns", "corr", "60d", "cross", "BTC–SPX beta"),
        FactorSpec("x_btc_gold_corr_20d", "20d corr BTC vs gold returns", "corr", "20d", "cross", "BTC–GOLD"),
        FactorSpec("x_btc_gold_corr_60d", "60d corr BTC vs gold returns", "corr", "60d", "cross", "BTC–GOLD"),
        FactorSpec("x_btc_dxy_corr_20d", "20d corr BTC vs DXY returns", "corr", "20d", "cross", "BTC–DXY"),
        FactorSpec("x_btc_dxy_corr_60d", "60d corr BTC vs DXY returns", "corr", "60d", "cross", "BTC–DXY"),
        FactorSpec("x_btc_us10y_corr_20d", "20d corr BTC returns vs 10Y changes", "corr", "20d", "cross", "BTC–US10Y"),
        FactorSpec("x_btc_us10y_corr_60d", "60d corr BTC returns vs 10Y changes", "corr", "60d", "cross", "BTC–US10Y"),
        FactorSpec("cal_fomc_flag", "1 on FOMC date ± window", "flag", "1d", "calendar", "FOMC calendar"),
        FactorSpec("cal_cpi_flag", "1 on CPI date ± window", "flag", "1d", "calendar", "CPI calendar"),
        FactorSpec("macro_hormuz_risk_flag", "Static Hormuz shipping-risk flag from CSV", "flag", "1d", "calendar", "oil / Hormuz"),
        FactorSpec("flow_btc_etf_net", "US spot BTC ETF daily net flow (USD mn, CSV)", "USD mn", "1d", "flow", "ETF flows / IBIT"),
        FactorSpec("px_ethbtc_ret_20d", "ETH/BTC 20d return", "fraction", "20d", "crypto-macro", "ETH/BTC rotation"),
        FactorSpec("px_btc_dominance_proxy", "BTC mcap / (BTC+ETH+SOL) using supply×price", "fraction", "1d", "crypto-macro", "BTC dominance proxy"),
        FactorSpec("px_korea_premium", "BTC-KRW / (BTC-USD * USDKRW) - 1", "fraction", "1d", "crypto-macro", "Korea premium"),
    ]
    for s in specs:
        register(s)


def _close(frames: dict[str, pd.DataFrame], ticker: str | None) -> pd.Series | None:
    if not ticker or ticker not in frames:
        return None
    df = frames[ticker]
    if df is None or df.empty or "close" not in df.columns:
        return None
    s = df["close"].astype(float)
    s.index = pd.DatetimeIndex(s.index).tz_localize(None).normalize()
    s = s[~s.index.duplicated(keep="last")]
    return s


def _align(series_map: dict[str, pd.Series]) -> pd.DataFrame:
    present = {k: v for k, v in series_map.items() if v is not None and len(v)}
    if not present:
        return pd.DataFrame()
    return pd.DataFrame(present).sort_index()


def compute_macro_factors(
    frames: dict[str, pd.DataFrame],
    ticker_map: dict[str, str],
    cfg: dict,
) -> pd.DataFrame:
    """Build a date × factor panel. Missing inputs → column omitted or NaN."""
    register_macro_specs()

    btc = _close(frames, "BTC-USD")
    eth = _close(frames, "ETH-USD")
    sol = _close(frames, "SOL-USD")
    us10y_raw = _close(frames, ticker_map.get("us10y"))
    us2y_raw = _close(frames, ticker_map.get("us2y"))
    us13w_raw = _close(frames, ticker_map.get("us13w"))
    dxy = _close(frames, ticker_map.get("dxy"))
    usdjpy = _close(frames, ticker_map.get("usdjpy"))
    wti = _close(frames, ticker_map.get("wti"))
    brent = _close(frames, ticker_map.get("brent"))
    gold = _close(frames, ticker_map.get("gold"))
    spx = _close(frames, ticker_map.get("spx"))
    ndx = _close(frames, ticker_map.get("ndx"))
    krw = _close(frames, ticker_map.get("krw"))
    btc_krw = _close(frames, ticker_map.get("btc_krw"))

    us10y = normalize_yield(us10y_raw) if us10y_raw is not None else None
    us2y = normalize_yield(us2y_raw) if us2y_raw is not None else None
    us13w = normalize_yield(us13w_raw) if us13w_raw is not None else None

    cols: dict[str, pd.Series] = {}

    if us10y is not None:
        cols["macro_us10y_level"] = us10y
        cols["macro_us10y_chg"] = change(us10y, 1)
        cols["macro_fed_restrictive_flag"] = (us10y > FED_RESTRICTIVE_THRESHOLD).astype(float)
    if us2y is not None:
        cols["macro_us2y_level"] = us2y
        cols["macro_us2y_chg"] = change(us2y, 1)
    if us13w is not None:
        cols["macro_us13w_level"] = us13w
        cols["macro_fed_funds_proxy"] = us13w
    if us10y is not None and us2y is not None:
        aligned = pd.concat({"t": us10y, "s": us2y}, axis=1).dropna()
        cols["macro_2s10s"] = aligned["t"] - aligned["s"]

    if dxy is not None:
        cols["macro_dxy_level"] = dxy
        cols["macro_dxy_ret_20d"] = returns(dxy, 20)
    if usdjpy is not None:
        cols["macro_usdjpy_ret_20d"] = returns(usdjpy, 20)
    if wti is not None:
        cols["macro_wti_ret_20d"] = returns(wti, 20)
    if brent is not None:
        cols["macro_brent_ret_20d"] = returns(brent, 20)
    oil_legs = [cols[k] for k in ("macro_wti_ret_20d", "macro_brent_ret_20d") if k in cols]
    if oil_legs:
        cols["macro_oil_ret_20d"] = pd.concat(oil_legs, axis=1).mean(axis=1)
    if gold is not None:
        cols["macro_gold_ret_20d"] = returns(gold, 20)
    if spx is not None:
        cols["macro_spx_ret_20d"] = returns(spx, 20)
    if ndx is not None:
        cols["macro_ndx_ret_20d"] = returns(ndx, 20)

    if btc is not None:
        cols["px_btc_dist_200dma"] = ma_distance(btc, 200)
        cols["px_btc_dist_365dma"] = ma_distance(btc, 365)
        cols["px_btc_rv_30d"] = close_to_close_vol(btc, 30)
        cols["px_btc_rv_90d"] = close_to_close_vol(btc, 90)
    if eth is not None:
        cols["px_eth_dist_200dma"] = ma_distance(eth, 200)
        cols["px_eth_dist_365dma"] = ma_distance(eth, 365)
        cols["px_eth_rv_30d"] = close_to_close_vol(eth, 30)
    if btc is not None and eth is not None:
        ethbtc = (eth / btc.replace(0.0, pd.NA)).dropna()
        cols["px_ethbtc_ret_20d"] = returns(ethbtc, 20)

    supplies = (cfg or {}).get("supplies") or {}
    if btc is not None and eth is not None and sol is not None:
        mb = btc * float(supplies.get("BTC-USD", 19_700_000))
        me = eth * float(supplies.get("ETH-USD", 120_500_000))
        ms = sol * float(supplies.get("SOL-USD", 470_000_000))
        tot = mb + me + ms
        cols["px_btc_dominance_proxy"] = mb / tot.replace(0.0, pd.NA)

    if btc is not None and krw is not None and btc_krw is not None:
        implied = btc * krw
        cols["px_korea_premium"] = btc_krw / implied.replace(0.0, pd.NA) - 1.0

    def _xcorr(other: pd.Series | None, short_id: str, long_id: str, other_is_yield: bool = False) -> None:
        if btc is None or other is None:
            return
        a = returns(btc, 1)
        b = change(other, 1) if other_is_yield else returns(other, 1)
        pair = pd.concat({"a": a, "b": b}, axis=1).dropna()
        cols[short_id] = rolling_corr(pair["a"], pair["b"], 20)
        cols[long_id] = rolling_corr(pair["a"], pair["b"], 60)

    _xcorr(spx, "x_btc_spx_corr_20d", "x_btc_spx_corr_60d")
    _xcorr(gold, "x_btc_gold_corr_20d", "x_btc_gold_corr_60d")
    _xcorr(dxy, "x_btc_dxy_corr_20d", "x_btc_dxy_corr_60d")
    _xcorr(us10y, "x_btc_us10y_corr_20d", "x_btc_us10y_corr_60d", other_is_yield=True)

    panel = _align(cols)
    if panel.empty:
        logger.warning("macro panel empty — no overlapping price history")
        return panel

    cal_cfg = (cfg or {}).get("calendar") or {}
    window = int(cal_cfg.get("event_window_days", 1))
    events = load_event_table(cal_cfg.get("fixture"))
    panel["cal_fomc_flag"] = event_flags(panel.index, events, "FOMC", window).reindex(panel.index).fillna(0.0)
    panel["cal_cpi_flag"] = event_flags(panel.index, events, "CPI", window).reindex(panel.index).fillna(0.0)
    panel["macro_hormuz_risk_flag"] = hormuz_flag(
        panel.index, load_hormuz_table(cal_cfg.get("hormuz_fixture"))
    ).reindex(panel.index).fillna(0.0)

    etf_cfg = (cfg or {}).get("etf_flows") or {}
    flows = load_etf_flows(
        etf_cfg.get("csv_path"),
        date_col=etf_cfg.get("date_col", "date"),
        value_col=etf_cfg.get("value_col", "net_flow_usd_mn"),
    )
    panel["flow_btc_etf_net"] = align_etf_flows(panel.index, flows)

    return panel.sort_index()
