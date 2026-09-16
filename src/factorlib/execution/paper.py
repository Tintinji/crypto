"""In-memory paper exchange. Never opens a network connection."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from factorlib.execution.adapter import OrderIntent, OrderResult


class PaperNetworkError(RuntimeError):
    """Raised if anything tries to touch the network from the paper adapter."""


class PaperAdapter:
    """Spot-style paper book. Prices come from an injected last_price map."""

    name = "paper"

    def __init__(
        self,
        *,
        cash_usd: float = 10_000.0,
        last_prices: dict[str, float] | None = None,
        spread_bps: float = 2.0,
    ):
        self.cash_usd = float(cash_usd)
        self.last_prices = dict(last_prices or {})
        self.spread_bps = float(spread_bps)
        self.positions: dict[str, float] = {}  # base qty
        self.orders: list[dict[str, Any]] = []
        self.realized_pnl_today = 0.0
        self._network_calls = 0  # must stay 0

    def _touch_network(self) -> None:
        self._network_calls += 1
        raise PaperNetworkError("paper adapter must not hit the network")

    def set_price(self, symbol: str, price: float) -> None:
        self.last_prices[symbol] = float(price)

    def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        px = float(self.last_prices.get(symbol) or self.last_prices.get(symbol.replace("/", "-"), 0.0))
        if px <= 0:
            raise KeyError(f"no paper price for {symbol}; inject last_prices")
        half = px * (self.spread_bps / 20_000.0)
        return {
            "symbol": symbol,
            "last": px,
            "bid": px - half,
            "ask": px + half,
            "spread_bps": self.spread_bps,
        }

    def fetch_balance(self) -> dict[str, Any]:
        return {"USD": self.cash_usd, "USDT": self.cash_usd, "free": {"USDT": self.cash_usd}}

    def fetch_position_notional(self, symbol: str) -> float:
        qty = self.positions.get(symbol, 0.0)
        ticker = self.fetch_ticker(symbol)
        return float(qty) * float(ticker["last"])

    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ticker = self.fetch_ticker(symbol)
        px = float(price) if (order_type == "limit" and price) else float(ticker["last"])
        qty = float(amount)
        notional = qty * px
        if side == "buy":
            self.cash_usd -= notional
            self.positions[symbol] = self.positions.get(symbol, 0.0) + qty
        elif side == "sell":
            self.cash_usd += notional
            self.positions[symbol] = self.positions.get(symbol, 0.0) - qty
        else:
            raise ValueError(f"unknown side {side}")
        rec = {
            "id": uuid4().hex,
            "symbol": symbol,
            "type": order_type,
            "side": side,
            "amount": qty,
            "price": px,
            "status": "closed",
            "filled": qty,
            "params": params or {},
        }
        self.orders.append(rec)
        return rec

    def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        for o in self.orders:
            if o["id"] == order_id and o["symbol"] == symbol:
                o["status"] = "canceled"
                return o
        return {"id": order_id, "symbol": symbol, "status": "not_found"}

    def fill_intent(self, intent: OrderIntent) -> OrderResult:
        raw = self.create_order(
            intent.symbol,
            intent.order_type,
            intent.side,
            intent.amount,
            intent.price,
            {"reduceOnly": intent.reduce_only} if intent.reduce_only else None,
        )
        return OrderResult(
            ok=True,
            intent=intent,
            exchange_order_id=str(raw["id"]),
            status=str(raw["status"]),
            filled=float(raw["filled"]),
            avg_price=float(raw["price"]),
            raw=raw,
        )
