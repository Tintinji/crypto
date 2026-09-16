"""Factor screening is point-in-time; selected IDs stay inside the registry."""

from __future__ import annotations

import numpy as np
import pandas as pd

from factorlib.cli.main import build_parser, cmd_screen_factors
from factorlib.macro.compute import register_macro_specs
from factorlib.model.scoring import zscore_panel
from factorlib.model.screening import (
    ScreenConfig,
    build_screened_weights,
    evaluate_factor,
    forward_returns,
    rolling_spearman,
    run_screen,
    select_factors,
    spearman_ic,
)
from factorlib.pricevolume.compute import register_pv_specs
from factorlib.registry import list_factor_ids


def _close(n: int = 200, seed: int = 1) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n)
    px = 20_000 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, n)))
    return pd.Series(px, index=idx, name="close")


def test_forward_return_is_next_bar_not_same_bar():
    idx = pd.bdate_range("2024-01-02", periods=6)
    close = pd.Series([100.0, 110.0, 100.0, 100.0, 130.0, 130.0], index=idx)
    fwd = forward_returns(close, horizon=1, signal_lag=1)
    # Signal on first day uses 110/100-1, not a same-bar 0.
    assert np.isclose(fwd.iloc[0], 0.10)
    # Same-bar return of day 1 would be +10%; we must not pair that with day-1 signal.
    assert not np.isclose(fwd.iloc[1], 0.10)
    assert np.isclose(fwd.iloc[1], 100.0 / 110.0 - 1.0)
    fwd5 = forward_returns(close, horizon=5, signal_lag=1)
    assert np.isclose(fwd5.iloc[0], 130.0 / 100.0 - 1.0)


def test_zscore_and_rolling_ic_ignore_future_factor():
    close = _close(80, seed=3)
    idx = close.index
    factor = pd.Series(np.linspace(-1, 1, len(idx)), index=idx)
    z_full = zscore_panel(factor.to_frame("f"), min_periods=10, expanding=True)["f"]
    cut = 40
    z_pref = zscore_panel(factor.iloc[: cut + 1].to_frame("f"), min_periods=10, expanding=True)["f"]
    assert np.isclose(float(z_full.iloc[cut]), float(z_pref.iloc[-1]), rtol=1e-12, atol=1e-12)

    fwd = forward_returns(close, 1, 1)
    ic_full = rolling_spearman(z_full, fwd, window=20, min_periods=10)
    shocked = factor.copy()
    shocked.iloc[-1] = 50.0
    z_shock = zscore_panel(shocked.to_frame("f"), min_periods=10, expanding=True)["f"]
    ic_shock = rolling_spearman(z_shock, fwd, window=20, min_periods=10)
    # Windows that end before the last bar must be unchanged.
    assert np.allclose(ic_full.iloc[:-1].fillna(0), ic_shock.iloc[:-1].fillna(0), atol=1e-12)
    # Prefix IC at cut equals full-sample IC at cut (window only uses ≤ cut).
    ic_pref = rolling_spearman(z_pref, fwd.iloc[: cut + 1], window=20, min_periods=10)
    a, b = ic_full.iloc[cut], ic_pref.iloc[-1]
    if pd.notna(a) and pd.notna(b):
        assert np.isclose(float(a), float(b), rtol=1e-12, atol=1e-12)


def test_evaluate_factor_ic_window_uses_past_z_only():
    close = _close(90, seed=4)
    signal = close.pct_change().shift(1)  # PIT: yesterday's return
    z = zscore_panel(signal.to_frame("s"), min_periods=8, expanding=True)["s"]
    row = evaluate_factor(z, close, ScreenConfig(min_obs=20, oos_days=20, rolling_ic_window=15))
    assert row["n_obs"] >= 20
    assert np.isfinite(row["ic_spearman"])


def test_selected_ids_are_registry_subset():
    register_macro_specs()
    register_pv_specs()
    ids = set(list_factor_ids())
    close = _close(220, seed=5)
    rng = np.random.default_rng(5)
    idx = close.index
    # Strong: tomorrow's return leaked into a fake factor — used only to test plumbing,
    # plus two noisy columns and a correlated clone.
    fwd = forward_returns(close, 1, 1)
    panel = pd.DataFrame(
        {
            "px_btc_mom_20": fwd.shift(-1).fillna(0.0) + rng.normal(0, 0.01, len(idx)),
            "px_btc_mom_60": fwd.shift(-1).fillna(0.0) + rng.normal(0, 0.012, len(idx)),
            "macro_dxy_ret_20d": rng.normal(0, 1, len(idx)),
            "not_a_factor": rng.normal(0, 1, len(idx)),
        },
        index=idx,
    )
    # Make mom_60 almost equal to mom_20 so corr cluster drops one.
    panel["px_btc_mom_60"] = panel["px_btc_mom_20"] * 0.98 + rng.normal(0, 0.001, len(idx))
    cfg = ScreenConfig(min_obs=30, oos_days=40, icir_threshold=0.05, rolling_ic_window=20)
    result = run_screen(panel, close, cfg, registry_ids=ids)
    assert set(result.selected) <= ids
    assert "not_a_factor" not in result.selected
    dropped_ids = {d["id"] for d in result.dropped}
    assert "not_a_factor" in dropped_ids


def test_select_factors_drops_weaker_of_corr_cluster():
    metrics = pd.DataFrame(
        {
            "icir_is": [1.2, 0.9, 0.05],
            "ic_is": [0.1, 0.08, 0.01],
            "ic_oos": [0.06, 0.05, -0.02],
            "same_sign_is_oos": [True, True, False],
            "turnover": [0.1, 0.1, 0.1],
        },
        index=["strong", "clone", "weak"],
    )
    corr = pd.DataFrame(
        [[1.0, 0.95, 0.1], [0.95, 1.0, 0.1], [0.1, 0.1, 1.0]],
        index=metrics.index,
        columns=metrics.index,
    )
    cfg = ScreenConfig(icir_threshold=0.3, corr_threshold=0.7)
    kept, dropped = select_factors(metrics, corr, cfg, allowed=list(metrics.index))
    assert kept == ["strong"]
    reasons = {d["id"]: d["reason"] for d in dropped}
    assert reasons["clone"] == "redundant_corr"
    assert reasons["weak"] == "oos_sign_mismatch"
    weights = build_screened_weights(kept, metrics, "icir")
    assert weights["strong"] > 0


def test_parser_has_screen_factors():
    p = build_parser()
    args = p.parse_args(["screen-factors", "--skip-backtest"])
    assert args.func is cmd_screen_factors
    assert args.skip_backtest is True


def test_cli_screen_smoke(tmp_path, monkeypatch):
    close = _close(90, seed=8)
    rng = np.random.default_rng(8)
    panel = pd.DataFrame(
        {
            "px_btc_mom_20": close.pct_change(20),
            "macro_dxy_ret_20d": rng.normal(0, 0.02, len(close)),
        },
        index=close.index,
    )

    class _Store:
        def load(self):
            return panel

        def factor_ids(self):
            return ["px_btc_mom_20", "macro_dxy_ret_20d"]

    monkeypatch.setattr("factorlib.cli.main.FactorStore", lambda cfg: _Store())
    monkeypatch.setattr(
        "factorlib.cli.main.read_ohlcv",
        lambda _t: pd.DataFrame({"close": close}),
    )
    monkeypatch.setattr("factorlib.model.screening.factor_screen_dir", lambda: tmp_path)
    monkeypatch.setattr("factorlib.cli.main.persist_screen", lambda result, out_dir=None: tmp_path)

    args = build_parser().parse_args(["screen-factors", "--skip-backtest"])
    rc = cmd_screen_factors({"model": {"target_symbol": "BTC-USD", "weights": {}}}, args)
    assert rc == 0
