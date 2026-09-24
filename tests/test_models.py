from datetime import datetime, timezone

import pytest

from datatech.domain.models import ProductSnapshot


def test_snapshot_normalizes_title_and_serializes():
    snapshot = ProductSnapshot(
        source="mercadolibre",
        source_product_id="MLA123",
        title="  Placa Gráfica RTX 5070!!! ",
        price=1000,
        currency="ARS",
        url="https://example.test/item",
        captured_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
    )
    assert snapshot.normalized_title == "placa grafica rtx 5070"
    assert snapshot.to_document()["price"] == 1000.0


def test_snapshot_rejects_negative_prices():
    with pytest.raises(ValueError):
        ProductSnapshot(
            source="x",
            source_product_id="1",
            title="item",
            price=-1,
            currency="USD",
            url="https://example.test",
        )
