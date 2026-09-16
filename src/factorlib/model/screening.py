"""Point-in-time factor screening: Rank IC, ICIR, clusters, walk-forward, selection.

Research only — not financial advice. Screening a short crypto sample will overfit
if you treat the selected set as a fitted alpha.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from factorlib.data.store import factor_screen_dir, write_frame
from factorlib.model.backtest import run_backtest
from factorlib.model.metrics import format_metrics, save_metrics, summarize
from factorlib.model.scoring import zscore_panel


@dataclass
class ScreenConfig:
    icir_threshold: float = 0.3
    oos_days: int = 126
    corr_threshold: float = 0.7
    horizons: tuple[int, ...] = (1, 5, 20)
    rolling_ic_window: int = 63
    min_obs: int = 60
    turnover_penalty: bool = False
    turnover_cap: float = 0.35
    weight_scheme: str = "icir"  # icir | equal_risk | equal
    signal_lag: int = 1
    zscore_window: int = 126
    zscore_min_periods: int = 20
    expanding: bool = True
    z_clip: float = 3.0
    nw_lags: int | None = None
    cost_bps: float = 15.0
    primary_horizon: int = 1

    @classmethod
    def from_cfg(cls, cfg: dict[str, Any] | None) -> ScreenConfig:
        model = (cfg or {}).get("model") or {}
        raw = (cfg or {}).get("screen") or {}
        horizons = raw.get("horizons", (1, 5, 20))
        return cls(
            icir_threshold=float(raw.get("icir_threshold", 0.3)),
            oos_days=int(raw.get("oos_days", 126)),
            corr_threshold=float(raw.get("corr_threshold", 0.7)),
            horizons=tuple(int(h) for h in horizons),
            rolling_ic_window=int(raw.get("rolling_ic_window", 63)),
            min_obs=int(raw.get("min_obs", 60)),
            turnover_penalty=bool(raw.get("turnover_penalty", False)),
            turnover_cap=float(raw.get("turnover_cap", 0.35)),
            weight_scheme=str(raw.get("weight_scheme", "icir")),
            signal_lag=int(raw.get("signal_lag", model.get("signal_lag", 1))),
            zscore_window=int(raw.get("zscore_window", model.get("zscore_window", 126))),
            zscore_min_periods=int(
                raw.get("zscore_min_periods", model.get("zscore_min_periods", 20))
            ),
            expanding=bool(raw.get("expanding", model.get("expanding", True))),
            z_clip=float(raw.get("z_clip", model.get("z_clip", 3.0))),
            nw_lags=raw.get("nw_lags"),
            cost_bps=float(raw.get("cost_bps", model.get("cost_bps", 15))),
            primary_horizon=int(raw.get("primary_horizon", 1)),
        )


@dataclass
class ScreenResult:
    metrics: pd.DataFrame
    z_panel: pd.DataFrame
    corr: pd.DataFrame
    clusters: list[dict[str, Any]]
    selected: list[str]
    dropped: list[dict[str, Any]]
    weights: dict[str, float]
    config: ScreenConfig
    split: dict[str, str]
    comparison: dict[str, dict] = field(default_factory=dict)


def _normalize_index(idx) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(idx).tz_localize(None).normalize()


def forward_returns(close: pd.Series, horizon: int, signal_lag: int = 1) -> pd.Series:
    """Return realized *after* the signal bar, aligned to the signal date.

    Signal at close of date t is traded on bar t+``signal_lag``. Horizon-h
    simple return is close[t+lag+h-1] / close[t+lag-1] - 1.

    For the default lag=1, h=1 this is the next-bar return close[t+1]/close[t]-1
    and does **not** use the contemporaneous close-to-close return of date t.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    if signal_lag < 1:
        raise ValueError("signal_lag must be >= 1")
    px = close.astype(float).copy()
    px.index = _normalize_index(px.index)
    px = px[~px.index.duplicated(keep="last")].sort_index()
    start = px.shift(1 - signal_lag)  # lag=1 → close[t]
    end = px.shift(1 - signal_lag - horizon)  # lag=1,h=1 → close[t+1]
    fwd = end / start.replace(0.0, np.nan) - 1.0
    fwd.name = f"fwd_{horizon}d"
    return fwd


def spearman_ic(factor: pd.Series, fwd: pd.Series) -> float:
    df = pd.concat({"f": factor, "r": fwd}, axis=1).dropna()
    if len(df) < 3:
        return float("nan")
    if df["f"].nunique() < 2 or df["r"].nunique() < 2:
        return float("nan")
    return float(df["f"].rank().corr(df["r"].rank()))


def rolling_spearman(factor: pd.Series, fwd: pd.Series, window: int, min_periods: int | None = None) -> pd.Series:
    """Rolling Spearman using only rows inside [t-window+1, t]. Factor is assumed PIT."""
    mp = min_periods if min_periods is not None else max(10, window // 3)
    df = pd.concat({"f": factor.astype(float), "r": fwd.astype(float)}, axis=1).sort_index()
    out = pd.Series(np.nan, index=df.index, dtype=float)
    f = df["f"].to_numpy(dtype=float, copy=False)
    r = df["r"].to_numpy(dtype=float, copy=False)
    n = len(df)
    for i in range(n):
        lo = 0 if window <= 0 else max(0, i - window + 1)
        sl_f = f[lo : i + 1]
        sl_r = r[lo : i + 1]
        mask = np.isfinite(sl_f) & np.isfinite(sl_r)
        if int(mask.sum()) < mp:
            continue
        a = sl_f[mask]
        b = sl_r[mask]
        if np.unique(a).size < 2 or np.unique(b).size < 2:
            continue
        out.iloc[i] = float(pd.Series(a).rank().corr(pd.Series(b).rank()))
    out.name = "rolling_ic"
    return out


def _nw_lag(n: int, explicit: int | None) -> int:
    if explicit is not None:
        return max(0, int(explicit))
    if n < 8:
        return 0
    return max(1, int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0))))


def newey_west_mean_tstat(series: pd.Series, lags: int | None = None) -> float:
    """HAC t-stat of mean(series)."""
    x = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    n = int(x.size)
    if n < 5:
        return float("nan")
    mu = float(x.mean())
    L = _nw_lag(n, lags)
    demean = x - mu
    gamma0 = float(np.dot(demean, demean) / n)
    hac = gamma0
    for lag in range(1, L + 1):
        w = 1.0 - lag / (L + 1.0)
        gamma = float(np.dot(demean[lag:], demean[:-lag]) / n)
        hac += 2.0 * w * gamma
    se = np.sqrt(hac / n) if hac > 0 else 0.0
    return float(mu / se) if se > 0 else float("nan")


def newey_west_ols_tstat(y: pd.Series, x: pd.Series, lags: int | None = None) -> tuple[float, float]:
    """OLS y = a + b x with Newey-West t-stat on slope b. Returns (beta, tstat)."""
    df = pd.concat({"y": y, "x": x}, axis=1).dropna()
    n = len(df)
    if n < 8:
        return float("nan"), float("nan")
    Y = df["y"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(n), df["x"].to_numpy(dtype=float)])
    try:
        beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    except np.linalg.LinAlgError:
        return float("nan"), float("nan")
    resid = Y - X @ beta
    L = _nw_lag(n, lags)
    k = 2
    meat = np.zeros((k, k))
    for t in range(n):
        xt = X[t]
        meat += (resid[t] ** 2) * np.outer(xt, xt)
    for lag in range(1, L + 1):
        w = 1.0 - lag / (L + 1.0)
        g = np.zeros((k, k))
        for t in range(lag, n):
            g += resid[t] * resid[t - lag] * np.outer(X[t], X[t - lag])
        meat += w * (g + g.T)
    try:
        xtx_inv = np.linalg.inv(X.T @ X)
        var = xtx_inv @ meat @ xtx_inv
        se = float(np.sqrt(max(var[1, 1], 0.0)))
    except np.linalg.LinAlgError:
        return float(beta[1]), float("nan")
    tstat = float(beta[1] / se) if se > 0 else float("nan")
    return float(beta[1]), tstat


def hit_rate(factor: pd.Series, fwd: pd.Series) -> float:
    df = pd.concat({"f": factor, "r": fwd}, axis=1).dropna()
    if df.empty:
        return float("nan")
    sf = np.sign(df["f"].to_numpy(dtype=float))
    sr = np.sign(df["r"].to_numpy(dtype=float))
    mask = (sf != 0) & (sr != 0)
    if not mask.any():
        return float("nan")
    return float((sf[mask] == sr[mask]).mean())


def signed_turnover(factor: pd.Series) -> float:
    """Mean |Δ position| of a simple signed exposure pos = sign(z), 0 if z is NaN."""
    pos = np.sign(factor.astype(float)).fillna(0.0)
    return float(pos.diff().abs().fillna(pos.abs()).mean())


def _is_oos_masks(
    index: pd.DatetimeIndex,
    oos_days: int,
    signal_lag: int,
    horizon: int,
) -> tuple[pd.Series, pd.Series, pd.Timestamp]:
    idx = _normalize_index(index)
    if len(idx) <= oos_days + 5:
        oos_start = idx[max(1, len(idx) // 2)]
    else:
        oos_start = idx[-int(oos_days)]
    # Clean IS: forward return must fully realize before oos_start.
    last_is = oos_start - pd.Timedelta(days=int(signal_lag + horizon))
    is_mask = pd.Series(idx <= last_is, index=idx)
    oos_mask = pd.Series(idx >= oos_start, index=idx)
    return is_mask, oos_mask, pd.Timestamp(oos_start)


def _safe_float(x: Any) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    if not np.isfinite(v):
        return float("nan")
    return v


def evaluate_factor(
    z: pd.Series,
    close: pd.Series,
    cfg: ScreenConfig,
    *,
    regime: pd.Series | None = None,
) -> dict[str, Any]:
    """IC / ICIR / decay / hit / turnover for one PIT z-scored factor."""
    fwd_map = {h: forward_returns(close, h, cfg.signal_lag) for h in cfg.horizons}
    primary = int(cfg.primary_horizon)
    if primary not in fwd_map:
        primary = cfg.horizons[0]
    fwd = fwd_map[primary]
    aligned = pd.concat({"z": z, "fwd": fwd}, axis=1).dropna()
    n = len(aligned)
    row: dict[str, Any] = {
        "n_obs": int(n),
        "ic_spearman": float("nan"),
        "icir": float("nan"),
        "ic_tstat_nw": float("nan"),
        "ols_beta": float("nan"),
        "ols_tstat_nw": float("nan"),
        "hit_rate": float("nan"),
        "turnover": float("nan"),
        "ic_is": float("nan"),
        "ic_oos": float("nan"),
        "icir_is": float("nan"),
        "icir_oos": float("nan"),
        "same_sign_is_oos": False,
        "factor_vol": float("nan"),
        "ic_restrictive": float("nan"),
        "ic_nonrestrictive": float("nan"),
        "ic_high_vol": float("nan"),
        "ic_low_vol": float("nan"),
    }
    for h in cfg.horizons:
        row[f"ic_{h}d"] = float("nan")
    if n < cfg.min_obs:
        return row

    z_a = aligned["z"]
    f_a = aligned["fwd"]
    row["ic_spearman"] = spearman_ic(z_a, f_a)
    row["hit_rate"] = hit_rate(z_a, f_a)
    row["turnover"] = signed_turnover(z)
    row["factor_vol"] = float(z_a.std(ddof=0))
    roll = rolling_spearman(z_a, f_a, cfg.rolling_ic_window)
    roll_v = roll.dropna()
    if len(roll_v) >= 5 and float(roll_v.std(ddof=0)) > 0:
        row["icir"] = float(roll_v.mean() / roll_v.std(ddof=0))
        row["ic_tstat_nw"] = newey_west_mean_tstat(roll_v, cfg.nw_lags)
    else:
        # Fallback: Newey-West t-stat of OLS / sqrt(n) style ICIR proxy
        row["icir"] = float("nan")
        row["ic_tstat_nw"] = newey_west_mean_tstat(z_a * f_a, cfg.nw_lags)
    beta, tstat = newey_west_ols_tstat(f_a, z_a, cfg.nw_lags)
    row["ols_beta"] = beta
    row["ols_tstat_nw"] = tstat

    for h, series in fwd_map.items():
        row[f"ic_{h}d"] = spearman_ic(z, series)

    is_mask, oos_mask, _oos_start = _is_oos_masks(aligned.index, cfg.oos_days, cfg.signal_lag, primary)
    is_mask = is_mask.reindex(aligned.index).fillna(False)
    oos_mask = oos_mask.reindex(aligned.index).fillna(False)
    z_is, f_is = z_a.loc[is_mask], f_a.loc[is_mask]
    z_oos, f_oos = z_a.loc[oos_mask], f_a.loc[oos_mask]
    row["ic_is"] = spearman_ic(z_is, f_is)
    row["ic_oos"] = spearman_ic(z_oos, f_oos)
    roll_is = rolling_spearman(z_is, f_is, cfg.rolling_ic_window).dropna()
    roll_oos = rolling_spearman(z_oos, f_oos, min(cfg.rolling_ic_window, max(20, len(z_oos) // 2))).dropna()
    if len(roll_is) >= 5 and float(roll_is.std(ddof=0)) > 0:
        row["icir_is"] = float(roll_is.mean() / roll_is.std(ddof=0))
    if len(roll_oos) >= 5 and float(roll_oos.std(ddof=0)) > 0:
        row["icir_oos"] = float(roll_oos.mean() / roll_oos.std(ddof=0))
    if np.isfinite(row["ic_is"]) and np.isfinite(row["ic_oos"]) and row["ic_is"] != 0 and row["ic_oos"] != 0:
        row["same_sign_is_oos"] = bool(np.sign(row["ic_is"]) == np.sign(row["ic_oos"]))

    if regime is not None:
        flag = regime.reindex(aligned.index)
        on = flag.fillna(0.0) > 0
        row["ic_restrictive"] = spearman_ic(z_a.loc[on], f_a.loc[on])
        row["ic_nonrestrictive"] = spearman_ic(z_a.loc[~on], f_a.loc[~on])

    return {k: (_safe_float(v) if k not in {"n_obs", "same_sign_is_oos"} else v) for k, v in row.items()}


def pairwise_z_corr(z_panel: pd.DataFrame, min_obs: int = 40) -> pd.DataFrame:
    cols = list(z_panel.columns)
    corr = pd.DataFrame(np.nan, index=cols, columns=cols, dtype=float)
    for i, a in enumerate(cols):
        corr.loc[a, a] = 1.0
        for b in cols[i + 1 :]:
            pair = pd.concat({"a": z_panel[a], "b": z_panel[b]}, axis=1).dropna()
            if len(pair) < min_obs:
                continue
            if pair["a"].std(ddof=0) == 0 or pair["b"].std(ddof=0) == 0:
                continue
            c = float(pair["a"].corr(pair["b"]))
            corr.loc[a, b] = c
            corr.loc[b, a] = c
    return corr


def corr_clusters(corr: pd.DataFrame, threshold: float = 0.7) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            c = corr.loc[a, b]
            if pd.notna(c) and abs(float(c)) > threshold:
                pairs.append({"a": a, "b": b, "corr": float(c)})
    pairs.sort(key=lambda p: -abs(p["corr"]))
    return pairs


def select_factors(
    metrics: pd.DataFrame,
    corr: pd.DataFrame,
    cfg: ScreenConfig,
    allowed: Iterable[str] | None = None,
) -> tuple[list[str], list[dict[str, Any]]]:
    """|ICIR_IS| >= threshold, OOS IC same sign as IS, then drop weaker of |corr|>thr pairs."""
    dropped: list[dict[str, Any]] = []
    allow = set(allowed) if allowed is not None else None
    candidates: list[str] = []
    for fid, row in metrics.iterrows():
        fid = str(fid)
        if allow is not None and fid not in allow:
            dropped.append({"id": fid, "reason": "not_in_registry"})
            continue
        icir = _safe_float(row.get("icir_is", np.nan))
        if not np.isfinite(icir):
            icir = _safe_float(row.get("icir", np.nan))
        if not np.isfinite(icir) or abs(icir) < cfg.icir_threshold:
            dropped.append({"id": fid, "reason": "icir_below_threshold", "icir_is": icir})
            continue
        if not bool(row.get("same_sign_is_oos", False)):
            dropped.append(
                {
                    "id": fid,
                    "reason": "oos_sign_mismatch",
                    "ic_is": _safe_float(row.get("ic_is")),
                    "ic_oos": _safe_float(row.get("ic_oos")),
                }
            )
            continue
        if cfg.turnover_penalty and _safe_float(row.get("turnover")) > cfg.turnover_cap:
            dropped.append(
                {
                    "id": fid,
                    "reason": "turnover_cap",
                    "turnover": _safe_float(row.get("turnover")),
                }
            )
            continue
        candidates.append(fid)

    def _strength(fid: str) -> float:
        icir = _safe_float(metrics.loc[fid].get("icir_is", np.nan))
        if not np.isfinite(icir):
            icir = _safe_float(metrics.loc[fid].get("icir", np.nan))
        return abs(icir) if np.isfinite(icir) else 0.0

    candidates.sort(key=_strength, reverse=True)
    kept: list[str] = []
    for fid in candidates:
        redundant_of = None
        for k in kept:
            if fid in corr.index and k in corr.columns:
                c = corr.loc[fid, k]
                if pd.notna(c) and abs(float(c)) > cfg.corr_threshold:
                    redundant_of = k
                    break
        if redundant_of is not None:
            dropped.append(
                {
                    "id": fid,
                    "reason": "redundant_corr",
                    "kept": redundant_of,
                    "corr": float(corr.loc[fid, redundant_of]),
                }
            )
            continue
        kept.append(fid)
    return kept, dropped


def build_screened_weights(
    selected: list[str],
    metrics: pd.DataFrame,
    scheme: str = "icir",
) -> dict[str, float]:
    weights: dict[str, float] = {}
    for fid in selected:
        row = metrics.loc[fid]
        ic = _safe_float(row.get("ic_is", np.nan))
        if not np.isfinite(ic):
            ic = _safe_float(row.get("ic_spearman", np.nan))
        sign = 1.0 if (not np.isfinite(ic) or ic >= 0) else -1.0
        if scheme == "equal":
            w = sign
        elif scheme == "equal_risk":
            vol = _safe_float(row.get("factor_vol", 1.0))
            w = sign / max(vol, 0.1)
        else:
            icir = _safe_float(row.get("icir_is", np.nan))
            if not np.isfinite(icir):
                icir = _safe_float(row.get("icir", np.nan))
            w = sign * abs(icir if np.isfinite(icir) else 1.0)
        weights[fid] = float(w)
    return weights


def equal_weight_all(panel: pd.DataFrame, min_obs: int = 20) -> dict[str, float]:
    return {c: 1.0 for c in panel.columns if int(panel[c].notna().sum()) >= min_obs}


def buy_and_hold_metrics(close: pd.Series, cost_bps: float = 15.0) -> dict[str, float]:
    px = close.astype(float).copy()
    px.index = _normalize_index(px.index)
    ret = px.pct_change()
    cost = pd.Series(0.0, index=ret.index)
    valid = ret.dropna()
    if not valid.empty:
        cost.loc[valid.index[0]] = cost_bps / 10_000.0
    metrics = summarize(ret - cost)
    metrics["cost_bps"] = float(cost_bps)
    metrics["signal_lag"] = 0
    metrics["expanding"] = False
    return metrics


def _high_vol_flag(panel: pd.DataFrame, min_periods: int = 20) -> pd.Series | None:
    """PIT high-vol regime: RV > expanding median (no future vol in the threshold)."""
    col = "px_btc_rv_30d" if "px_btc_rv_30d" in panel.columns else None
    if col is None:
        return None
    rv = panel[col].astype(float)
    med = rv.expanding(min_periods=min_periods).median()
    return (rv > med).astype(float)


def run_screen(
    panel: pd.DataFrame,
    close: pd.Series,
    cfg: ScreenConfig | None = None,
    *,
    registry_ids: Iterable[str] | None = None,
) -> ScreenResult:
    cfg = cfg or ScreenConfig()
    if panel.empty:
        raise ValueError("factor panel is empty — run compute-factors first")
    work = panel.copy()
    work.index = _normalize_index(work.index)
    work = work[~work.index.duplicated(keep="last")].sort_index()
    z = zscore_panel(
        work,
        window=cfg.zscore_window,
        min_periods=cfg.zscore_min_periods,
        expanding=cfg.expanding,
        z_clip=cfg.z_clip,
    )
    restrictive = work["macro_fed_restrictive_flag"] if "macro_fed_restrictive_flag" in work.columns else None
    high_vol = _high_vol_flag(work, cfg.zscore_min_periods)
    rows: dict[str, dict[str, Any]] = {}
    for col in z.columns:
        ev = evaluate_factor(z[col], close, cfg, regime=restrictive)
        if high_vol is not None:
            fwd = forward_returns(close, cfg.primary_horizon, cfg.signal_lag)
            aligned = pd.concat({"z": z[col], "fwd": fwd, "hv": high_vol}, axis=1).dropna()
            on = aligned["hv"] > 0
            ev["ic_high_vol"] = spearman_ic(aligned.loc[on, "z"], aligned.loc[on, "fwd"])
            ev["ic_low_vol"] = spearman_ic(aligned.loc[~on, "z"], aligned.loc[~on, "fwd"])
        rows[col] = ev
    metrics = pd.DataFrame.from_dict(rows, orient="index")
    metrics.index.name = "factor_id"
    metrics = metrics.sort_values(by=["icir_is", "ic_oos"], ascending=False, na_position="last")

    is_mask, oos_mask, oos_start = _is_oos_masks(z.index, cfg.oos_days, cfg.signal_lag, cfg.primary_horizon)
    z_is = z.loc[is_mask.reindex(z.index).fillna(False)]
    corr = pairwise_z_corr(z_is if len(z_is) > cfg.min_obs else z, min_obs=max(20, cfg.min_obs // 2))
    clusters = corr_clusters(corr, cfg.corr_threshold)
    selected, dropped = select_factors(metrics, corr, cfg, allowed=registry_ids)
    weights = build_screened_weights(selected, metrics, cfg.weight_scheme)
    split = {
        "oos_start": str(pd.Timestamp(oos_start).date()),
        "start": str(pd.Timestamp(work.index.min()).date()) if len(work) else "",
        "end": str(pd.Timestamp(work.index.max()).date()) if len(work) else "",
        "n_days": str(int(len(work))),
        "oos_days": str(int(cfg.oos_days)),
    }
    return ScreenResult(
        metrics=metrics,
        z_panel=z,
        corr=corr,
        clusters=clusters,
        selected=selected,
        dropped=dropped,
        weights=weights,
        config=cfg,
        split=split,
    )


def persist_screen(result: ScreenResult, out_dir: Path | None = None) -> Path:
    dest = Path(out_dir) if out_dir is not None else factor_screen_dir()
    dest.mkdir(parents=True, exist_ok=True)
    write_frame(result.metrics, dest / "factor_metrics.parquet")
    result.metrics.to_csv(dest / "factor_metrics.csv")
    write_frame(result.corr, dest / "corr_matrix.parquet")
    result.corr.to_csv(dest / "corr_matrix.csv")
    payload = {
        "disclaimer": "research only — not financial advice",
        "split": result.split,
        "config": asdict(result.config),
        "selected": result.selected,
        "weights": result.weights,
        "dropped": result.dropped,
        "clusters": result.clusters,
        "n_factors": int(len(result.metrics)),
        "n_selected": int(len(result.selected)),
        "n_clusters": int(len(result.clusters)),
    }
    (dest / "selected.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    (dest / "clusters.json").write_text(json.dumps(result.clusters, indent=2), encoding="utf-8")
    return dest


def run_comparison_backtests(
    panel: pd.DataFrame,
    close: pd.Series,
    *,
    default_weights: dict[str, float],
    screened_weights: dict[str, float],
    cfg: ScreenConfig,
    persist: bool = True,
    out_dir: Path | None = None,
) -> dict[str, dict]:
    dest = Path(out_dir) if out_dir is not None else factor_screen_dir()
    common = dict(
        cost_bps=cfg.cost_bps,
        signal_lag=cfg.signal_lag,
        zscore_window=cfg.zscore_window,
        zscore_min_periods=cfg.zscore_min_periods,
        expanding=cfg.expanding,
        z_clip=cfg.z_clip,
        persist=persist,
        out_dir=dest if persist else None,
    )
    comparison: dict[str, dict] = {}
    _, m_default = run_backtest(panel, close, default_weights, stem="equity_default", **common)
    comparison["default"] = m_default
    eq_w = equal_weight_all(panel)
    _, m_equal = run_backtest(panel, close, eq_w, stem="equity_equal_all", **common)
    comparison["equal_all"] = m_equal
    if screened_weights:
        _, m_scr = run_backtest(panel, close, screened_weights, stem="equity_screened", **common)
    else:
        m_scr = {
            "cagr": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "max_dd": 0.0,
            "hit_rate": 0.0,
            "n_obs": 0,
            "total_return": 0.0,
            "note": "no factors selected",
        }
    comparison["screened"] = m_scr
    comparison["buy_hold"] = buy_and_hold_metrics(close, cfg.cost_bps)
    if persist:
        dest.mkdir(parents=True, exist_ok=True)
        save_metrics(comparison, dest / "comparison.json")
        lines = ["research only — not financial advice", ""]
        for name, met in comparison.items():
            if "cagr" in met:
                lines.append(f"{name:12s}  {format_metrics(met)}")
        (dest / "comparison.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return comparison


def format_metrics_table(metrics: pd.DataFrame, ids: list[str] | None = None, extra_cols: list[str] | None = None) -> str:
    cols = extra_cols or [
        "icir_is",
        "ic_is",
        "ic_oos",
        "ic_spearman",
        "ic_1d",
        "ic_5d",
        "ic_20d",
        "ic_tstat_nw",
        "hit_rate",
        "turnover",
        "same_sign_is_oos",
        "n_obs",
    ]
    use = metrics if ids is None else metrics.loc[[i for i in ids if i in metrics.index]]
    keep = [c for c in cols if c in use.columns]
    return use[keep].to_string(float_format=lambda x: f"{x: .4f}")
