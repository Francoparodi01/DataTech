from __future__ import annotations

import re
import time
from datetime import UTC, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from datatech.domain.models import ProductSnapshot

_PRICE = re.compile(r"[^0-9.,]")


def _parse_price(text: str) -> float | None:
    value = _PRICE.sub("", text).strip()
    if not value:
        return None
    if "," in value and "." in value:
        value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


class AmazonHtmlCollector:
    """Small fallback collector. Prefer Amazon Creators API when credentials are available."""

    def __init__(
        self,
        *,
        marketplace: str = "https://www.amazon.com",
        currency: str = "USD",
        timeout: float = 20,
        user_agent: str = "Mozilla/5.0 DataTech/0.2",
        delay_seconds: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        self.marketplace = marketplace.rstrip("/")
        self.currency = currency
        self.timeout = timeout
        self.delay_seconds = max(0.0, delay_seconds)
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def parse_page(
        self,
        html: str,
        *,
        captured_at: datetime | None = None,
    ) -> list[ProductSnapshot]:
        captured_at = captured_at or datetime.now(UTC)
        soup = BeautifulSoup(html, "html.parser")
        snapshots: list[ProductSnapshot] = []
        for card in soup.select('[data-component-type="s-search-result"][data-asin]'):
            asin = (card.get("data-asin") or "").strip()
            title_el = card.select_one("h2 span")
            link_el = card.select_one("h2 a")
            price_el = card.select_one(".a-price .a-offscreen")
            image_el = card.select_one("img.s-image")
            if not asin or title_el is None or link_el is None or price_el is None:
                continue
            price = _parse_price(price_el.get_text(" ", strip=True))
            if price is None:
                continue
            href = link_el.get("href") or ""
            snapshots.append(
                ProductSnapshot(
                    source="amazon",
                    source_product_id=asin,
                    title=title_el.get_text(" ", strip=True),
                    price=price,
                    currency=self.currency,
                    url=urljoin(self.marketplace, href),
                    image_url=image_el.get("src") if image_el else None,
                    captured_at=captured_at,
                )
            )
        return snapshots

    def search(self, query: str, *, max_pages: int = 1) -> list[ProductSnapshot]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        captured_at = datetime.now(UTC)
        snapshots: list[ProductSnapshot] = []
        for page in range(1, max_pages + 1):
            response = self.session.get(
                f"{self.marketplace}/s",
                params={"k": query, "page": page},
                timeout=self.timeout,
            )
            response.raise_for_status()
            parsed = self.parse_page(response.text, captured_at=captured_at)
            snapshots.extend(parsed)
            if not parsed:
                break
            if page < max_pages and self.delay_seconds:
                time.sleep(self.delay_seconds)
        return snapshots
