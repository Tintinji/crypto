"""Paper adapter must never open a network connection."""

from __future__ import annotations

import socket

import pytest

from factorlib.execution.paper import PaperAdapter, PaperNetworkError
from factorlib.execution.router import execute_intent, score_to_intent
from factorlib.risk.gates import RiskGate


def test_paper_order_with_socket_disabled(monkeypatch):
    def blocked(*_a, **_k):
        raise AssertionError("paper adapter opened a socket")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "socket", lambda *a, **k: (_ for _ in ()).throw(AssertionError("socket()")))

    adapter = PaperAdapter(cash_usd=10_000, last_prices={"BTC/USDT": 60_000.0})
    ticker = adapter.fetch_ticker("BTC/USDT")
    assert ticker["last"] == 60_000.0
    bal = adapter.fetch_balance()
    assert bal["USDT"] == 10_000.0
    raw = adapter.create_order("BTC/USDT", "market", "buy", 0.001)
    assert raw["status"] == "closed"
    assert adapter._network_calls == 0


def test_paper_touch_network_helper_raises():
    adapter = PaperAdapter(last_prices={"BTC/USDT": 1.0})
    with pytest.raises(PaperNetworkError):
        adapter._touch_network()


def test_score_to_intent_and_paper_fill():
    adapter = PaperAdapter(last_prices={"BTC/USDT": 40_000.0})
    gate = RiskGate(
        max_notional_usd=100,
        max_position_usd=200,
        max_daily_loss_usd=50,
        max_spread_bps=50,
    )
    intent = score_to_intent(
        0.5,
        symbol="BTC/USDT",
        last_price=40_000.0,
        default_notional_usd=80,
        mode="paper",
    )
    assert intent.side == "buy"
    assert intent.notional_usd == 40.0
    result = execute_intent(adapter, gate, intent, spread_bps=2.0)
    assert result.ok is True
    assert adapter.fetch_position_notional("BTC/USDT") > 0


def test_limit_and_reduce_only_params():
    adapter = PaperAdapter(last_prices={"ETH/USDT": 2_000.0})
    intent = score_to_intent(
        -0.25,
        symbol="ETH/USDT",
        last_price=2_000.0,
        default_notional_usd=100,
        order_type="limit",
        limit_offset_bps=10,
        reduce_only=True,
        mode="paper",
    )
    assert intent.side == "sell"
    assert intent.price is not None
    assert intent.price < 2_000.0
    raw = adapter.create_order(
        intent.symbol,
        intent.order_type,
        intent.side,
        intent.amount,
        intent.price,
        {"reduceOnly": True},
    )
    assert raw["params"]["reduceOnly"] is True
