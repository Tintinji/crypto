"""Hard risk gate + kill switch. No new orders when blocked."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from factorlib.paths import REPO_ROOT


def kill_switch_active(kill_file: str | Path = "KILL") -> bool:
    if os.environ.get("KILL_SWITCH", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        return True
    candidates = [
        Path(kill_file),
        REPO_ROOT / kill_file,
        Path.cwd() / "KILL",
        REPO_ROOT / "KILL",
    ]
    return any(p.exists() for p in candidates)


@dataclass
class RiskDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)

    def raise_if_blocked(self) -> None:
        if not self.allowed:
            raise PermissionError("risk gate blocked order: " + "; ".join(self.reasons))


class RiskGate:
    """Rejects new orders that breach notional, position, daily loss, spread, or kill."""

    def __init__(
        self,
        *,
        max_notional_usd: float,
        max_position_usd: float,
        max_daily_loss_usd: float,
        max_spread_bps: float,
        kill_file: str = "KILL",
        leverage_cap: float = 1.0,
    ):
        self.max_notional_usd = float(max_notional_usd)
        self.max_position_usd = float(max_position_usd)
        self.max_daily_loss_usd = float(max_daily_loss_usd)
        self.max_spread_bps = float(max_spread_bps)
        self.kill_file = kill_file
        self.leverage_cap = float(leverage_cap)

    def check(
        self,
        *,
        notional_usd: float,
        position_usd_after: float,
        daily_pnl_usd: float,
        spread_bps: float | None = None,
        leverage: float | None = None,
        reduce_only: bool = False,
    ) -> RiskDecision:
        reasons: list[str] = []
        if kill_switch_active(self.kill_file):
            reasons.append("kill switch active (KILL file or KILL_SWITCH=1)")

        notion = abs(float(notional_usd))
        if notion > self.max_notional_usd + 1e-9:
            reasons.append(
                f"notional {notion:.2f} exceeds max_notional_usd {self.max_notional_usd:.2f}"
            )

        if abs(float(position_usd_after)) > self.max_position_usd + 1e-9:
            reasons.append(
                f"|position| {abs(position_usd_after):.2f} exceeds max_position_usd {self.max_position_usd:.2f}"
            )

        if float(daily_pnl_usd) <= -abs(self.max_daily_loss_usd) + 1e-9:
            reasons.append(
                f"daily pnl {daily_pnl_usd:.2f} hit max_daily_loss_usd {self.max_daily_loss_usd:.2f}"
            )

        if spread_bps is not None and float(spread_bps) > self.max_spread_bps + 1e-9:
            reasons.append(
                f"spread {spread_bps:.2f} bps exceeds max_spread_bps {self.max_spread_bps:.2f}"
            )

        if leverage is not None and float(leverage) > self.leverage_cap + 1e-9:
            reasons.append(f"leverage {leverage:.2f} exceeds cap {self.leverage_cap:.2f}")

        # reduce-only still blocked by kill / daily loss / spread — never "new risk" but
        # kill means flatten only via a dedicated flatten path, not this gate's new orders.
        _ = reduce_only
        return RiskDecision(allowed=not reasons, reasons=reasons)
