from __future__ import annotations

from factorlib.cli.main import cmd_live_order
from factorlib.data.config import load_config
from factorlib.execution.ccxt_live import LiveConfigError
from factorlib.execution.router import build_adapter, live_enabled


class _Args:
    i_understand_live = False


def test_live_enabled_requires_exact_env(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    assert live_enabled() is False
    monkeypatch.setenv("LIVE_TRADING", "1")
    assert live_enabled() is True
    monkeypatch.setenv("LIVE_TRADING", "true")
    assert live_enabled() is False


def test_build_adapter_live_refuses_without_env(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    cfg = load_config()
    try:
        build_adapter(cfg, mode="live")
        raise AssertionError("should have refused")
    except LiveConfigError as exc:
        assert "LIVE_TRADING" in str(exc)


def test_cli_live_refuses_without_flag_and_env(monkeypatch):
    monkeypatch.delenv("LIVE_TRADING", raising=False)
    cfg = load_config()
    rc = cmd_live_order(cfg, _Args())
    assert rc == 2


def test_cli_live_refuses_without_acknowledge(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING", "1")
    cfg = load_config()
    args = _Args()
    args.i_understand_live = False
    rc = cmd_live_order(cfg, args)
    assert rc == 2
