"""ccxt live adapter. Credentials come only from environment variables."""

from __future__ import annotations

import os
from typing import Any


class LiveConfigError(RuntimeError):
    pass


def env_credentials() -> dict[str, str]:
    return {
        "exchange_id": os.environ.get("EXCHANGE_ID", "binance").strip().lower(),
        "api_key": os.environ.get("EXCHANGE_API_KEY", "").strip(),
        "secret": os.environ.get("EXCHANGE_SECRET", "").strip(),
        "password": os.environ.get("EXCHANGE_PASSWORD", "").strip(),
        "sandbox": os.environ.get("EXCHANGE_SANDBOX", "").strip(),
        "market_type": os.environ.get("EXCHANGE_MARKET_TYPE", "").strip(),
    }


class CcxtAdapter:
    name = "ccxt"

    def __init__(
        self,
        *,
        exchange_id: str | None = None,
        market_type: str = "spot",
        leverage_cap: float = 1.0,
    ):
        creds = env_credentials()
        ex_id = (exchange_id or creds["exchange_id"] or "binance").lower()
        if not creds["api_key"] or not creds["secret"]:
            raise LiveConfigError(
                "EXCHANGE_API_KEY and EXCHANGE_SECRET must be set for live trading"
            )
        try:
            import ccxt  # local import so paper path never needs a live session
        except Exception as exc:  # noqa: BLE001
            raise LiveConfigError(f"ccxt import failed: {exc}") from exc
        if not hasattr(ccxt, ex_id):
            raise LiveConfigError(f"unknown ccxt exchange id: {ex_id}")
        klass = getattr(ccxt, ex_id)
        opts: dict[str, Any] = {
            "apiKey": creds["api_key"],
            "secret": creds["secret"],
            "enableRateLimit": True,
        }
        if creds["password"]:
            opts["password"] = creds["password"]
        if market_type and market_type != "spot":
            opts["options"] = {"defaultType": market_type}
        self.ex = klass(opts)
        if creds["sandbox"] in {"1", "true", "TRUE", "yes"}:
            if hasattr(self.ex, "set_sandbox_mode"):
                self.ex.set_sandbox_mode(True)
        self.market_type = market_type or creds["market_type"] or "spot"
        self.leverage_cap = float(leverage_cap)
        self.exchange_id = ex_id

    def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        t = self.ex.fetch_ticker(symbol)
        bid = t.get("bid")
        ask = t.get("ask")
        last = t.get("last") or t.get("close")
        spread_bps = None
        if bid and ask and (bid + ask) > 0:
            spread_bps = (float(ask) - float(bid)) / ((float(ask) + float(bid)) / 2.0) * 10_000.0
        return {
            "symbol": symbol,
            "last": last,
            "bid": bid,
            "ask": ask,
            "spread_bps": spread_bps,
            "raw": t,
        }

    def fetch_balance(self) -> dict[str, Any]:
        return self.ex.fetch_balance()

    def fetch_position_notional(self, symbol: str) -> float:
        if self.market_type == "spot":
            bal = self.fetch_balance()
            base = symbol.split("/")[0]
            free = ((bal.get("free") or {}).get(base)) or 0.0
            total = ((bal.get("total") or {}).get(base)) or free
            px = float(self.fetch_ticker(symbol)["last"] or 0.0)
            return float(total or 0.0) * px
        # futures: isolated positions when supported
        if hasattr(self.ex, "fetch_positions"):
            positions = self.ex.fetch_positions([symbol])
            notion = 0.0
            for p in positions or []:
                notion += abs(float(p.get("notional") or p.get("contracts") or 0.0))
            return notion
        return 0.0

    def _maybe_set_leverage(self, symbol: str) -> None:
        if self.market_type == "spot":
            return
        cap = min(max(self.leverage_cap, 1.0), 2.0)
        try:
            if hasattr(self.ex, "set_margin_mode"):
                self.ex.set_margin_mode("isolated", symbol)
        except Exception:
            pass
        try:
            if hasattr(self.ex, "set_leverage"):
                self.ex.set_leverage(int(cap), symbol)
        except Exception:
            pass

    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._maybe_set_leverage(symbol)
        p = dict(params or {})
        return self.ex.create_order(symbol, order_type, side, amount, price, p)

    def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        return self.ex.cancel_order(order_id, symbol)
