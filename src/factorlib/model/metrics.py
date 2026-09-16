"""Backtest performance metrics."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak.replace(0.0, np.nan) - 1.0
    return float(dd.min()) if len(dd) else 0.0


def summarize(net: pd.Series, periods_per_year: int = 365) -> dict[str, float]:
    r = net.dropna().astype(float)
    if r.empty:
        return {
            "cagr": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "max_dd": 0.0,
            "hit_rate": 0.0,
            "n_obs": 0,
            "total_return": 0.0,
        }
    eq = (1.0 + r).cumprod()
    n = len(r)
    years = n / float(periods_per_year)
    total = float(eq.iloc[-1] - 1.0)
    cagr = float(eq.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and eq.iloc[-1] > 0 else 0.0
    vol = float(r.std(ddof=0) * np.sqrt(periods_per_year))
    sharpe = float((r.mean() / r.std(ddof=0)) * np.sqrt(periods_per_year)) if r.std(ddof=0) > 0 else 0.0
    hits = r[r != 0.0]
    hit_rate = float((hits > 0).mean()) if len(hits) else 0.0
    return {
        "cagr": cagr,
        "vol": vol,
        "sharpe": sharpe,
        "max_dd": max_drawdown(eq),
        "hit_rate": hit_rate,
        "n_obs": int(n),
        "total_return": total,
    }


def save_metrics(metrics: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return path


def format_metrics(metrics: dict) -> str:
    return (
        f"CAGR={metrics['cagr']:.2%}  vol={metrics['vol']:.2%}  "
        f"Sharpe={metrics['sharpe']:.2f}  maxDD={metrics['max_dd']:.2%}  "
        f"hit={metrics['hit_rate']:.2%}  n={metrics['n_obs']}"
    )
