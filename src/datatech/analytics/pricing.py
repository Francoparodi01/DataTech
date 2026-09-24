from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import timedelta
from statistics import median

from datatech.domain.models import ProductSnapshot


@dataclass(frozen=True, slots=True)
class PriceSummary:
    current_price: float
    observations: int
    median_7d: float | None
    median_30d: float | None
    median_90d: float | None
    percentile: float
    change_from_first_pct: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _window_median(history: list[ProductSnapshot], days: int) -> float | None:
    if not history:
        return None
    cutoff = history[-1].captured_at - timedelta(days=days)
    values = [item.price for item in history if item.captured_at >= cutoff]
    return float(median(values)) if values else None


def summarize_price_history(history: list[ProductSnapshot]) -> PriceSummary:
    if not history:
        raise ValueError("history cannot be empty")
    history = sorted(history, key=lambda item: item.captured_at)
    current = history[-1].price
    values = [item.price for item in history]
    percentile = sum(value <= current for value in values) / len(values)
    first = history[0].price
    change = None if first == 0 else ((current - first) / first) * 100
    return PriceSummary(
        current_price=current,
        observations=len(history),
        median_7d=_window_median(history, 7),
        median_30d=_window_median(history, 30),
        median_90d=_window_median(history, 90),
        percentile=percentile,
        change_from_first_pct=change,
    )
