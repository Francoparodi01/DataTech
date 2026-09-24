from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import requests

from datatech.domain.models import ProductSnapshot


class MercadoLibreCollector:
    """Collector backed by Mercado Libre's public site search API."""

    api_base = "https://api.mercadolibre.com"

    def __init__(
        self,
        *,
        site_id: str = "MLA",
        timeout: float = 20,
        user_agent: str = "DataTech/0.2",
        session: requests.Session | None = None,
    ) -> None:
        self.site_id = site_id.upper()
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})

    def search(self, query: str, *, max_pages: int = 1, page_size: int = 50) -> list[ProductSnapshot]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        if max_pages < 1:
            raise ValueError("max_pages must be >= 1")
        page_size = max(1, min(page_size, 50))
        captured_at = datetime.now(timezone.utc)
        snapshots: list[ProductSnapshot] = []

        for page in range(max_pages):
            response = self.session.get(
                f"{self.api_base}/sites/{self.site_id}/search",
                params={"q": query, "limit": page_size, "offset": page * page_size},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            results: Iterable[dict] = payload.get("results") or []
            page_count = 0
            for item in results:
                product_id = str(item.get("id") or "").strip()
                title = str(item.get("title") or "").strip()
                price = item.get("price")
                currency = str(item.get("currency_id") or "").strip()
                url = str(item.get("permalink") or "").strip()
                if not product_id or not title or price is None or not currency or not url:
                    continue
                seller = item.get("seller") or {}
                snapshots.append(
                    ProductSnapshot(
                        source="mercadolibre",
                        source_product_id=product_id,
                        title=title,
                        price=float(price),
                        currency=currency,
                        url=url,
                        image_url=item.get("thumbnail"),
                        seller_id=str(seller.get("id")) if seller.get("id") is not None else None,
                        captured_at=captured_at,
                    )
                )
                page_count += 1
            if page_count == 0:
                break
        return snapshots
