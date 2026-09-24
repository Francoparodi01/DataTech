from __future__ import annotations

import requests

from datatech.analytics.deals import DealAssessment
from datatech.domain.models import ProductSnapshot


class WebhookAlertService:
    def __init__(self, webhook_url: str, *, timeout: float = 10) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send_if_needed(
        self,
        snapshot: ProductSnapshot,
        assessment: DealAssessment,
        *,
        threshold: float = 80,
    ) -> bool:
        if assessment.score < threshold:
            return False
        payload = {
            "text": (
                f"{assessment.label}: {snapshot.title} — {snapshot.currency} "
                f"{snapshot.price:.2f} — score {assessment.score:.1f}/100 — {snapshot.url}"
            ),
            "product": snapshot.to_document(),
            "assessment": assessment.to_dict(),
        }
        payload["product"]["captured_at"] = snapshot.captured_at.isoformat()
        response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return True
