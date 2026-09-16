"""Append-only JSONL of every intent and order result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factorlib.execution.adapter import utc_now_iso
from factorlib.paths import ensure_dir, repo_path


def orders_log_path() -> Path:
    return ensure_dir(repo_path("logs")) / "orders.jsonl"


def log_event(kind: str, payload: dict[str, Any]) -> None:
    rec = {"ts": utc_now_iso(), "kind": kind, **payload}
    path = orders_log_path()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
