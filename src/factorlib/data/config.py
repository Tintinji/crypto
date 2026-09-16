"""YAML config loader with env overlays."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from factorlib.paths import REPO_ROOT, repo_path


def _deep_get(d: dict, *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else repo_path("config", "default.yaml")
    if not cfg_path.is_absolute():
        cfg_path = REPO_ROOT / cfg_path
    with cfg_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    exec_cfg = cfg.setdefault("execution", {})
    env_ex = os.environ.get("EXCHANGE_ID")
    if env_ex:
        exec_cfg["exchange_id"] = env_ex
    if os.environ.get("EXCHANGE_MARKET_TYPE"):
        exec_cfg["market_type"] = os.environ["EXCHANGE_MARKET_TYPE"]
    if os.environ.get("LIVE_TRADING") == "1":
        exec_cfg["mode"] = "live"
    return cfg


def resolve_path(cfg_value: str | Path) -> Path:
    p = Path(cfg_value)
    return p if p.is_absolute() else REPO_ROOT / p


def get_in(cfg: dict, *keys: str, default: Any = None) -> Any:
    return _deep_get(cfg, *keys, default=default)


def overlay(base: dict, extra: dict | None) -> dict:
    out = deepcopy(base)
    if extra:
        out.update(extra)
    return out
