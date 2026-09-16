"""BTC ETF daily net-flow loader.

Official IBIT / US spot BTC ETF flows are *not* on yfinance.
Plug a Farside, SoSoValue, or issuer CSV via config `etf_flows.csv_path`.
A sample fixture ships under data/fixtures/btc_etf_flows.csv.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factorlib.data.config import resolve_path
from factorlib.paths import repo_path


def load_etf_flows(
    path: str | Path | None = None,
    date_col: str = "date",
    value_col: str = "net_flow_usd_mn",
) -> pd.Series:
    p = resolve_path(path) if path else repo_path("data", "fixtures", "btc_etf_flows.csv")
    if not Path(p).exists():
        return pd.Series(dtype=float, name="flow_btc_etf_net")
    df = pd.read_csv(p)
    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError(
            f"ETF flow CSV must contain columns '{date_col}' and '{value_col}'; got {list(df.columns)}"
        )
    s = pd.Series(
        pd.to_numeric(df[value_col], errors="coerce").values,
        index=pd.to_datetime(df[date_col]),
        name="flow_btc_etf_net",
    )
    s = s[~s.index.duplicated(keep="last")].sort_index()
    s.index = pd.DatetimeIndex(s.index).tz_localize(None).normalize()
    return s


def align_etf_flows(index: pd.DatetimeIndex, flows: pd.Series | None = None) -> pd.Series:
    """Align flows to a price calendar. Missing days = 0 (no print), not ffill of stale flow."""
    idx = pd.DatetimeIndex(index).tz_localize(None).normalize()
    src = flows if flows is not None else load_etf_flows()
    aligned = src.reindex(idx)
    # Weekend/holiday: no new print → 0. Do not forward-fill a prior day's flow.
    aligned = aligned.fillna(0.0)
    aligned.name = "flow_btc_etf_net"
    return aligned
