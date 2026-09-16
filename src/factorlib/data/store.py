"""Parquet/CSV persistence for OHLCV, factors, and scores."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factorlib.paths import ensure_dir, repo_path


def ohlcv_dir() -> Path:
    return ensure_dir(repo_path("data", "ohlcv"))


def factors_dir() -> Path:
    return ensure_dir(repo_path("data", "factors"))


def scores_dir() -> Path:
    return ensure_dir(repo_path("data", "scores"))


def backtest_dir() -> Path:
    return ensure_dir(repo_path("data", "backtests"))


def _safe_name(name: str) -> str:
    return (
        name.replace("^", "")
        .replace("/", "-")
        .replace("=", "_")
        .replace(".", "_")
    )


def ohlcv_path(ticker: str) -> Path:
    return ohlcv_dir() / f"{_safe_name(ticker)}.parquet"


def write_frame(df: pd.DataFrame, path: Path, *, index_name: str = "date") -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    out = df.copy()
    if out.index.name is None:
        out.index.name = index_name
    try:
        out.to_parquet(path)
    except Exception:
        csv_path = path.with_suffix(".csv")
        out.to_csv(csv_path)
        return csv_path
    return path


def read_frame(path: Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        csv_path = path.with_suffix(".csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            df.index = pd.DatetimeIndex(df.index).tz_localize(None)
            return df
        raise FileNotFoundError(path)
    df = pd.read_parquet(path)
    if not isinstance(df.index, pd.DatetimeIndex):
        if "date" in df.columns:
            df = df.set_index("date")
        df.index = pd.DatetimeIndex(df.index)
    df.index = pd.DatetimeIndex(df.index).tz_localize(None)
    return df.sort_index()


def write_ohlcv(ticker: str, df: pd.DataFrame) -> Path:
    return write_frame(df, ohlcv_path(ticker))


def read_ohlcv(ticker: str) -> pd.DataFrame:
    return read_frame(ohlcv_path(ticker))


def list_ohlcv_tickers() -> list[str]:
    names = []
    for p in ohlcv_dir().glob("*"):
        if p.suffix in {".parquet", ".csv"}:
            names.append(p.stem)
    return sorted(set(names))
