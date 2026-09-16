from __future__ import annotations

from factorlib.execution.adapter import OrderIntent
from factorlib.execution.paper import PaperAdapter
from factorlib.execution.router import execute_intent
from factorlib.risk.gates import RiskGate, kill_switch_active


def _gate(**kwargs) -> RiskGate:
    defaults = dict(
        max_notional_usd=100.0,
        max_position_usd=200.0,
        max_daily_loss_usd=25.0,
        max_spread_bps=10.0,
        kill_file="KILL",
        leverage_cap=1.0,
    )
    defaults.update(kwargs)
    return RiskGate(**defaults)


def test_blocks_over_notional():
    d = _gate().check(
        notional_usd=150,
        position_usd_after=150,
        daily_pnl_usd=0,
        spread_bps=1,
    )
    assert d.allowed is False
    assert any("notional" in r for r in d.reasons)


def test_blocks_over_position():
    d = _gate().check(
        notional_usd=50,
        position_usd_after=250,
        daily_pnl_usd=0,
        spread_bps=1,
    )
    assert d.allowed is False
    assert any("position" in r for r in d.reasons)


def test_blocks_daily_loss():
    d = _gate().check(
        notional_usd=10,
        position_usd_after=10,
        daily_pnl_usd=-25.0,
        spread_bps=1,
    )
    assert d.allowed is False
    assert any("daily pnl" in r for r in d.reasons)


def test_blocks_wide_spread():
    d = _gate().check(
        notional_usd=10,
        position_usd_after=10,
        daily_pnl_usd=0,
        spread_bps=50,
    )
    assert d.allowed is False
    assert any("spread" in r for r in d.reasons)


def test_blocks_leverage():
    d = _gate().check(
        notional_usd=10,
        position_usd_after=10,
        daily_pnl_usd=0,
        spread_bps=1,
        leverage=3,
    )
    assert d.allowed is False


def test_allows_small_ok_order():
    d = _gate().check(
        notional_usd=10,
        position_usd_after=10,
        daily_pnl_usd=0,
        spread_bps=2,
        leverage=1,
    )
    assert d.allowed is True
    assert d.reasons == []


def test_kill_switch_env(monkeypatch):
    monkeypatch.setenv("KILL_SWITCH", "1")
    assert kill_switch_active() is True
    d = _gate().check(notional_usd=1, position_usd_after=1, daily_pnl_usd=0, spread_bps=1)
    assert d.allowed is False
    assert any("kill" in r for r in d.reasons)


def test_kill_switch_file(tmp_path, monkeypatch):
    monkeypatch.delenv("KILL_SWITCH", raising=False)
    kill = tmp_path / "KILL"
    kill.write_text("stop\n")
    monkeypatch.chdir(tmp_path)
    assert kill_switch_active(kill) is True


def test_execute_intent_blocked_does_not_fill():
    adapter = PaperAdapter(last_prices={"BTC/USDT": 50_000})
    gate = _gate(max_notional_usd=10)
    intent = OrderIntent(
        symbol="BTC/USDT",
        side="buy",
        order_type="market",
        amount=1.0,
        notional_usd=50_000,
        mode="paper",
    )
    result = execute_intent(adapter, gate, intent, spread_bps=1.0)
    assert result.ok is False
    assert result.status == "blocked"
    assert adapter.positions.get("BTC/USDT", 0.0) == 0.0
