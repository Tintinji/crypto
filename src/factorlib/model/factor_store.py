"""Compute + persist the combined factor panel."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factorlib.data.store import factors_dir, read_frame, read_ohlcv, write_frame
from factorlib.macro.compute import compute_macro_factors, register_macro_specs
from factorlib.pricevolume.compute import compute_pricevolume_factors, register_pv_specs
from factorlib.registry import list_factor_ids


class FactorStore:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        register_macro_specs()
        register_pv_specs()

    @property
    def panel_path(self) -> Path:
        return factors_dir() / "panel.parquet"

    def load_frames(self, tickers: list[str] | None = None) -> dict[str, pd.DataFrame]:
        universe = self.cfg.get("universe") or {}
        crypto = list(universe.get("crypto") or ["BTC-USD", "ETH-USD", "SOL-USD"])
        macro_map = dict(universe.get("macro") or {})
        wanted = tickers or (crypto + list(macro_map.values()))
        frames: dict[str, pd.DataFrame] = {}
        for t in wanted:
            try:
                frames[t] = read_ohlcv(t)
            except FileNotFoundError:
                continue
        return frames

    def compute(self, frames: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
        frames = frames if frames is not None else self.load_frames()
        universe = self.cfg.get("universe") or {}
        crypto = list(universe.get("crypto") or ["BTC-USD", "ETH-USD", "SOL-USD"])
        ticker_map = dict(universe.get("macro") or {})
        macro = compute_macro_factors(frames, ticker_map, self.cfg)
        pv = compute_pricevolume_factors(frames, crypto)
        if macro.empty and pv.empty:
            return pd.DataFrame()
        if macro.empty:
            panel = pv
        elif pv.empty:
            panel = macro
        else:
            panel = macro.join(pv, how="outer")
        return panel.sort_index()

    def persist(self, panel: pd.DataFrame) -> Path:
        path = write_frame(panel, self.panel_path)
        # Also split wide CSV for eyeballing
        csv_path = factors_dir() / "panel.csv"
        panel.to_csv(csv_path)
        return path

    def load(self) -> pd.DataFrame:
        return read_frame(self.panel_path)

    def factor_ids(self) -> list[str]:
        return list_factor_ids()
