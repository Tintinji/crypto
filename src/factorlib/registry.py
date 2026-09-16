"""Central factor registry. Macro and price/volume modules register into this."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import pandas as pd


@dataclass(frozen=True)
class FactorSpec:
    id: str
    description: str
    unit: str
    horizon: str
    category: str
    narrative: str = ""
    compute: Callable[..., pd.Series] | None = field(default=None, compare=False, hash=False)


_REGISTRY: dict[str, FactorSpec] = {}


def register(spec: FactorSpec) -> FactorSpec:
    if spec.id in _REGISTRY:
        raise ValueError(f"duplicate factor id: {spec.id}")
    _REGISTRY[spec.id] = spec
    return spec


def get(factor_id: str) -> FactorSpec:
    return _REGISTRY[factor_id]


def all_specs() -> dict[str, FactorSpec]:
    return dict(_REGISTRY)


def list_factor_ids() -> list[str]:
    return sorted(_REGISTRY)


def list_factors(*, category: str | None = None) -> list[FactorSpec]:
    specs = list(_REGISTRY.values())
    if category:
        specs = [s for s in specs if s.category == category]
    return sorted(specs, key=lambda s: s.id)


def factor_catalog() -> list[dict[str, Any]]:
    return [
        {
            "id": s.id,
            "description": s.description,
            "unit": s.unit,
            "horizon": s.horizon,
            "category": s.category,
            "narrative": s.narrative,
        }
        for s in list_factors()
    ]
