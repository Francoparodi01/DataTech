from __future__ import annotations

from dataclasses import asdict, dataclass

from datatech.analytics.pricing import PriceSummary


@dataclass(frozen=True, slots=True)
class DealAssessment:
    score: float
    label: str
    confidence: float
    discount_vs_30d_pct: float | None
    discount_vs_90d_pct: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _discount(current: float, reference: float | None) -> float | None:
    if reference in (None, 0):
        return None
    return ((reference - current) / reference) * 100


def assess_deal(summary: PriceSummary) -> DealAssessment:
    discount_30 = _discount(summary.current_price, summary.median_30d)
    discount_90 = _discount(summary.current_price, summary.median_90d)

    score = 50.0
    if discount_30 is not None:
        score += max(-25.0, min(25.0, discount_30 * 2.0))
    if discount_90 is not None:
        score += max(-15.0, min(15.0, discount_90))
    score += max(-10.0, min(10.0, (0.5 - summary.percentile) * 20.0))
    score = round(max(0.0, min(100.0, score)), 1)

    if score >= 80:
        label = "STRONG_DEAL"
    elif score >= 65:
        label = "GOOD_DEAL"
    elif score >= 40:
        label = "NORMAL"
    else:
        label = "EXPENSIVE"

    return DealAssessment(
        score=score,
        label=label,
        confidence=round(min(1.0, summary.observations / 30.0), 2),
        discount_vs_30d_pct=discount_30,
        discount_vs_90d_pct=discount_90,
    )
