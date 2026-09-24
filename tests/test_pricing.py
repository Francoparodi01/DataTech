from datetime import UTC, datetime, timedelta

from datatech.analytics.deals import assess_deal
from datatech.analytics.pricing import summarize_price_history
from datatech.domain.models import ProductSnapshot


def _snapshot(day: int, price: float) -> ProductSnapshot:
    return ProductSnapshot(
        source="test",
        source_product_id="sku-1",
        title="GPU",
        price=price,
        currency="USD",
        url="https://example.test/gpu",
        captured_at=datetime(2026, 9, 1, tzinfo=UTC) + timedelta(days=day),
    )


def test_low_current_price_gets_positive_deal_signal():
    history = [_snapshot(i, 100 + i) for i in range(20)] + [_snapshot(20, 80)]
    summary = summarize_price_history(history)
    deal = assess_deal(summary)
    assert summary.current_price == 80
    assert summary.percentile <= 0.1
    assert deal.score >= 65
    assert deal.label in {"GOOD_DEAL", "STRONG_DEAL"}
