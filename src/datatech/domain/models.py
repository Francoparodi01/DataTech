from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from datatech.domain.normalization import normalize_title


@dataclass(frozen=True, slots=True)
class ProductSnapshot:
    source: str
    source_product_id: str
    title: str
    price: float
    currency: str
    url: str
    image_url: str | None = None
    seller_id: str | None = None
    rating: float | None = None
    review_count: int | None = None
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source is required")
        if not self.source_product_id.strip():
            raise ValueError("source_product_id is required")
        if not self.title.strip():
            raise ValueError("title is required")
        if self.price < 0:
            raise ValueError("price must be non-negative")
        if not self.currency.strip():
            raise ValueError("currency is required")
        if self.captured_at.tzinfo is None:
            raise ValueError("captured_at must be timezone-aware")

    @property
    def normalized_title(self) -> str:
        return normalize_title(self.title)

    def to_document(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_product_id": self.source_product_id,
            "title": self.title,
            "normalized_title": self.normalized_title,
            "price": float(self.price),
            "currency": self.currency,
            "url": self.url,
            "image_url": self.image_url,
            "seller_id": self.seller_id,
            "rating": self.rating,
            "review_count": self.review_count,
            "captured_at": self.captured_at,
        }

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "ProductSnapshot":
        captured_at = document["captured_at"]
        if captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=timezone.utc)
        return cls(
            source=document["source"],
            source_product_id=document["source_product_id"],
            title=document["title"],
            price=float(document["price"]),
            currency=document["currency"],
            url=document["url"],
            image_url=document.get("image_url"),
            seller_id=document.get("seller_id"),
            rating=document.get("rating"),
            review_count=document.get("review_count"),
            captured_at=captured_at,
        )
