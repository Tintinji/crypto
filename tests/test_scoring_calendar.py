from __future__ import annotations

import pandas as pd

from factorlib.data.calendar import event_flags, load_event_table
from factorlib.data.etf_flows import align_etf_flows, load_etf_flows
from factorlib.data.synthetic import make_ohlcv
from factorlib.macro.compute import compute_macro_factors
from factorlib.model.backtest import run_backtest
from factorlib.model.scoring import score_panel


def test_etf_fixture_loads():
    s = load_etf_flows()
    assert s.name == "flow_btc_etf_net"
    assert len(s) > 10
    assert s.abs().max() > 0


def test_etf_no_ffill_on_missing_days():
    idx = pd.bdate_range("2026-09-01", "2026-09-16")
    aligned = align_etf_flows(idx)
    # A date not in the fixture should be 0, not a carried prior flow.
    assert float(aligned.loc[pd.Timestamp("2026-09-07")]) == 0.0 or pd.Timestamp("2026-09-07").weekday() >= 5


def test_fomc_flag_window():
    events = load_event_table()
    idx = pd.bdate_range("2026-09-10", "2026-09-22")
    flag = event_flags(idx, events, "FOMC", window_days=1)
    # 2026-09-16 is in the static table
    assert flag.loc[pd.Timestamp("2026-09-16")] == 1.0


def test_score_and_backtest_offline():
    frames = {
        "BTC-USD": make_ohlcv("BTC-USD"),
        "ETH-USD": make_ohlcv("ETH-USD"),
        "SOL-USD": make_ohlcv("SOL-USD"),
        "^GSPC": make_ohlcv("^GSPC"),
        "DX-Y.NYB": make_ohlcv("DX-Y.NYB"),
        "^TNX": make_ohlcv("^TNX"),
        "GC=F": make_ohlcv("GC=F"),
        "CL=F": make_ohlcv("CL=F"),
        "BZ=F": make_ohlcv("BZ=F"),
    }
    cfg = {
        "supplies": {"BTC-USD": 19_700_000, "ETH-USD": 120_500_000, "SOL-USD": 470_000_000},
        "calendar": {},
        "etf_flows": {},
    }
    ticker_map = {
        "us10y": "^TNX",
        "dxy": "DX-Y.NYB",
        "gold": "GC=F",
        "wti": "CL=F",
        "brent": "BZ=F",
        "spx": "^GSPC",
    }
    panel = compute_macro_factors(frames, ticker_map, cfg)
    assert "flow_btc_etf_net" in panel.columns
    assert "macro_us10y_chg" in panel.columns
    weights = {"px_btc_dist_200dma": 0.5, "macro_dxy_ret_20d": -0.5, "flow_btc_etf_net": 0.2}
    # px_btc_dist is in macro compute
    score = score_panel(panel, weights, min_periods=10)
    assert score.abs().max() <= 1.0 + 1e-9
    _eq, metrics = run_backtest(
        panel,
        frames["BTC-USD"]["close"],
        weights,
        persist=False,
        zscore_min_periods=10,
    )
    assert "sharpe" in metrics
    assert metrics["n_obs"] > 50
