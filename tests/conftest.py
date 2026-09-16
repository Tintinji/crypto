from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_kill(tmp_path, monkeypatch):
    kill = tmp_path / "KILL"
    monkeypatch.chdir(tmp_path)
    return kill
