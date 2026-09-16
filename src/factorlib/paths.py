"""Repo-relative paths. All artifacts stay under the workspace."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_path(*parts: str | Path) -> Path:
    p = REPO_ROOT
    for part in parts:
        p = p / part
    return p


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
