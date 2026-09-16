"""Walk-forward / expanding-window backtest with transaction costs."""

from __future__ import annotations

import pandas as pd

from factorlib.data.store import backtest_dir, write_frame
from factorlib.model.metrics import format_metrics, save_metrics, summarize
from factorlib.model.scoring import score_panel


def run_backtest(
    panel: pd.DataFrame,
    close: pd.Series,
    weights: dict[str, float],
    *,
    cost_bps: float = 15.0,
    signal_lag: int = 1,
    zscore_window: int = 126,
    zscore_min_periods: int = 20,
    expanding: bool = True,
    z_clip: float = 3.0,
    persist: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Score uses data through t; position for return t+lag (default next bar).

    Costs: ``abs(delta position) * cost_bps / 1e4`` charged on the change bar.
    Crypto default 10–20 bps (config: 15).
    """
    score = score_panel(
        panel,
        weights,
        window=zscore_window,
        min_periods=zscore_min_periods,
        expanding=expanding,
        z_clip=z_clip,
    )
    px = close.astype(float)
    px.index = pd.DatetimeIndex(px.index).tz_localize(None).normalize()
    aligned = pd.concat({"score": score, "close": px}, axis=1).sort_index()
    aligned["ret"] = aligned["close"].pct_change()
    aligned["position"] = aligned["score"].shift(signal_lag).clip(-1.0, 1.0)
    aligned["gross"] = aligned["position"] * aligned["ret"]
    aligned["turnover"] = aligned["position"].diff().abs().fillna(aligned["position"].abs())
    aligned["cost"] = aligned["turnover"] * (cost_bps / 10_000.0)
    aligned["net"] = aligned["gross"] - aligned["cost"]
    aligned["equity"] = (1.0 + aligned["net"].fillna(0.0)).cumprod()

    # Expanding vs rolling is already in the score. Walk-forward label: expanding window.
    metrics = summarize(aligned["net"])
    metrics["cost_bps"] = float(cost_bps)
    metrics["signal_lag"] = int(signal_lag)
    metrics["expanding"] = bool(expanding)

    if persist:
        write_frame(aligned, backtest_dir() / "equity.parquet")
        aligned.to_csv(backtest_dir() / "equity.csv")
        save_metrics(metrics, backtest_dir() / "metrics.json")
        (backtest_dir() / "metrics.txt").write_text(format_metrics(metrics) + "\n", encoding="utf-8")

    return aligned, metrics
