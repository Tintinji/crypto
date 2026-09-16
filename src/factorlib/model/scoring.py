"""Time-series z-score combo → position target in [-1, 1]."""

from __future__ import annotations

import numpy as np
import pandas as pd


def zscore_panel(
    panel: pd.DataFrame,
    window: int = 126,
    min_periods: int = 20,
    expanding: bool = True,
    z_clip: float = 3.0,
) -> pd.DataFrame:
    """Point-in-time z-score. Expanding or rolling; no future mean/std."""
    x = panel.astype(float)
    if expanding:
        mu = x.expanding(min_periods=min_periods).mean()
        sd = x.expanding(min_periods=min_periods).std(ddof=0)
    else:
        mu = x.rolling(window, min_periods=min_periods).mean()
        sd = x.rolling(window, min_periods=min_periods).std(ddof=0)
    z = (x - mu) / sd.replace(0.0, np.nan)
    return z.clip(-z_clip, z_clip)


def score_panel(
    panel: pd.DataFrame,
    weights: dict[str, float],
    *,
    window: int = 126,
    min_periods: int = 20,
    expanding: bool = True,
    z_clip: float = 3.0,
) -> pd.Series:
    """Weighted sum of z-scored factors, then tanh → (-1, 1).

    Missing weight columns are skipped (live data holes should not crash).
    """
    use = {k: float(v) for k, v in weights.items() if k in panel.columns}
    if not use:
        return pd.Series(0.0, index=panel.index, name="score")
    z = zscore_panel(
        panel[list(use)],
        window=window,
        min_periods=min_periods,
        expanding=expanding,
        z_clip=z_clip,
    )
    raw = pd.Series(0.0, index=z.index)
    for col, w in use.items():
        raw = raw.add(z[col].fillna(0.0) * w, fill_value=0.0)
    # Scale by L1 of weights so typical |score| stays in range, then squash.
    denom = sum(abs(w) for w in use.values()) or 1.0
    score = np.tanh(raw / denom)
    score.name = "score"
    return score


def latest_score(scores: pd.Series) -> tuple[pd.Timestamp, float]:
    s = scores.dropna()
    if s.empty:
        raise ValueError("score series is empty — compute factors first")
    ts = s.index[-1]
    return pd.Timestamp(ts), float(s.iloc[-1])
