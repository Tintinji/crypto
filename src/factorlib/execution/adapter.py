"""Exchange adapter protocol + order records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OrderIntent:
    symbol: str
    side: str  # buy | sell
    order_type: str  # market | limit
    amount: float
    notional_usd: float
    price: float | None = None
    reduce_only: bool = False
    score: float | None = None
    mode: str = "paper"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OrderResult:
    ok: bool
    intent: OrderIntent
    exchange_order_id: str | None = None
    status: str = "rejected"
    filled: float = 0.0
    avg_price: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    ts: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["intent"] = self.intent.to_dict()
        return d


class ExchangeAdapter(Protocol):
    name: str

    def fetch_ticker(self, symbol: str) -> dict[str, Any]: ...

    def fetch_balance(self) -> dict[str, Any]: ...

    def fetch_position_notional(self, symbol: str) -> float: ...

    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]: ...
