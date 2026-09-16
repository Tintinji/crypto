"""FOMC / CPI / Hormuz event flags from a static table + loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factorlib.data.config import resolve_path
from factorlib.paths import repo_path


def load_event_table(path: str | Path | None = None) -> pd.DataFrame:
    p = resolve_path(path) if path else repo_path("data", "fixtures", "fomc_cpi_2026q4.csv")
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    df["event"] = df["event"].astype(str).str.upper().str.strip()
    return df


def load_hormuz_table(path: str | Path | None = None) -> pd.DataFrame:
    p = resolve_path(path) if path else repo_path("data", "fixtures", "hormuz_risk.csv")
    if not Path(p).exists():
        return pd.DataFrame(columns=["date", "hormuz_risk_flag"])
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    return df


def event_flags(
    index: pd.DatetimeIndex,
    events: pd.DataFrame,
    event_name: str,
    window_days: int = 1,
) -> pd.Series:
    """Point-in-time flag: 1 on event date and ±window calendar days."""
    idx = pd.DatetimeIndex(index).tz_localize(None).normalize()
    hits = events.loc[events["event"] == event_name.upper(), "date"]
    hits = pd.DatetimeIndex(pd.to_datetime(hits)).tz_localize(None).normalize()
    flag = pd.Series(0.0, index=idx, dtype=float)
    if hits.empty:
        flag.name = f"cal_{event_name.lower()}_flag"
        return flag
    for d in hits:
        lo = d - pd.Timedelta(days=window_days)
        hi = d + pd.Timedelta(days=window_days)
        mask = (flag.index >= lo) & (flag.index <= hi)
        flag.loc[mask] = 1.0
    flag.name = f"cal_{event_name.lower()}_flag"
    return flag


def hormuz_flag(index: pd.DatetimeIndex, table: pd.DataFrame | None = None) -> pd.Series:
    idx = pd.DatetimeIndex(index).tz_localize(None).normalize()
    flag = pd.Series(0.0, index=idx, dtype=float, name="macro_hormuz_risk_flag")
    tbl = table if table is not None else load_hormuz_table()
    if tbl.empty:
        return flag
    s = tbl.set_index("date")["hormuz_risk_flag"]
    s.index = pd.DatetimeIndex(s.index).normalize()
    aligned = s.reindex(idx).fillna(0.0).astype(float)
    aligned.name = "macro_hormuz_risk_flag"
    return aligned
