"""Score → sized intent → risk gate → adapter. Paper default; live is gated."""

from __future__ import annotations

import os
from typing import Any

from factorlib.execution.adapter import ExchangeAdapter, OrderIntent, OrderResult
from factorlib.execution.ccxt_live import CcxtAdapter, LiveConfigError
from factorlib.execution.journal import log_event
from factorlib.execution.paper import PaperAdapter
from factorlib.risk.gates import RiskGate


def live_enabled() -> bool:
    return os.environ.get("LIVE_TRADING", "").strip() == "1"


def score_to_intent(
    score: float,
    *,
    symbol: str,
    last_price: float,
    default_notional_usd: float,
    order_type: str = "market",
    limit_offset_bps: float = 5.0,
    reduce_only: bool = False,
    mode: str = "paper",
) -> OrderIntent:
    s = max(-1.0, min(1.0, float(score)))
    notion = abs(s) * float(default_notional_usd)
    side = "buy" if s >= 0 else "sell"
    amount = notion / float(last_price) if last_price else 0.0
    price = None
    if order_type == "limit" and last_price:
        off = float(limit_offset_bps) / 10_000.0
        price = last_price * (1.0 + off) if side == "buy" else last_price * (1.0 - off)
    return OrderIntent(
        symbol=symbol,
        side=side,
        order_type=order_type,
        amount=amount,
        notional_usd=notion,
        price=price,
        reduce_only=reduce_only,
        score=s,
        mode=mode,
    )


def execute_intent(
    adapter: ExchangeAdapter,
    gate: RiskGate,
    intent: OrderIntent,
    *,
    daily_pnl_usd: float = 0.0,
    position_usd_now: float | None = None,
    spread_bps: float | None = None,
    leverage: float | None = None,
) -> OrderResult:
    log_event("intent", {"intent": intent.to_dict()})
    pos_now = position_usd_now
    if pos_now is None:
        try:
            pos_now = float(adapter.fetch_position_notional(intent.symbol))
        except Exception:
            pos_now = 0.0
    signed = intent.notional_usd if intent.side == "buy" else -intent.notional_usd
    after = float(pos_now) + signed
    if spread_bps is None:
        try:
            t = adapter.fetch_ticker(intent.symbol)
            spread_bps = t.get("spread_bps")
        except Exception:
            spread_bps = None

    decision = gate.check(
        notional_usd=intent.notional_usd,
        position_usd_after=after,
        daily_pnl_usd=daily_pnl_usd,
        spread_bps=spread_bps,
        leverage=leverage,
        reduce_only=intent.reduce_only,
    )
    if not decision.allowed:
        result = OrderResult(
            ok=False,
            intent=intent,
            status="blocked",
            error="; ".join(decision.reasons),
        )
        log_event("blocked", result.to_dict())
        return result

    params: dict[str, Any] = {}
    if intent.reduce_only:
        params["reduceOnly"] = True
    try:
        raw = adapter.create_order(
            intent.symbol,
            intent.order_type,
            intent.side,
            intent.amount,
            intent.price,
            params or None,
        )
        result = OrderResult(
            ok=True,
            intent=intent,
            exchange_order_id=str(raw.get("id")) if raw else None,
            status=str(raw.get("status") or "submitted"),
            filled=float(raw.get("filled") or 0.0),
            avg_price=(float(raw["average"]) if raw.get("average") else raw.get("price")),
            raw=raw or {},
        )
        log_event("order", result.to_dict())
        return result
    except Exception as exc:  # noqa: BLE001
        result = OrderResult(ok=False, intent=intent, status="error", error=str(exc))
        log_event("error", result.to_dict())
        return result


def build_adapter(cfg: dict, *, mode: str, last_prices: dict[str, float] | None = None) -> ExchangeAdapter:
    exec_cfg = cfg.get("execution") or {}
    if mode == "paper":
        return PaperAdapter(
            cash_usd=float(exec_cfg.get("paper_cash_usd", 10_000)),
            last_prices=last_prices or {},
        )
    if not live_enabled():
        raise LiveConfigError("live adapter refused: set LIVE_TRADING=1")
    return CcxtAdapter(
        exchange_id=exec_cfg.get("exchange_id"),
        market_type=exec_cfg.get("market_type", "spot"),
        leverage_cap=float(exec_cfg.get("leverage_cap", 1)),
    )


def gate_from_cfg(cfg: dict) -> RiskGate:
    exec_cfg = cfg.get("execution") or {}
    risk_cfg = cfg.get("risk") or {}
    return RiskGate(
        max_notional_usd=float(exec_cfg.get("max_notional_usd", 200)),
        max_position_usd=float(exec_cfg.get("max_position_usd", 400)),
        max_daily_loss_usd=float(exec_cfg.get("max_daily_loss_usd", 40)),
        max_spread_bps=float(exec_cfg.get("max_spread_bps", 25)),
        kill_file=str(risk_cfg.get("kill_switch_file", "KILL")),
        leverage_cap=float(exec_cfg.get("leverage_cap", 1)),
    )
