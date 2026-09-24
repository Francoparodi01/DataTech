from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    mongodb_uri: str | None
    mongodb_database: str
    user_agent: str
    request_timeout: float
    alert_webhook_url: str | None
    flask_host: str
    flask_port: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mongodb_uri=os.getenv("MONGODB_URI") or None,
            mongodb_database=os.getenv("MONGODB_DATABASE", "datatech"),
            user_agent=os.getenv(
                "DATATECH_USER_AGENT",
                "DataTech/0.2 (+https://github.com/Francoparodi01/DataTech)",
            ),
            request_timeout=float(os.getenv("DATATECH_REQUEST_TIMEOUT", "20")),
            alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL") or None,
            flask_host=os.getenv("FLASK_HOST", "127.0.0.1"),
            flask_port=int(os.getenv("FLASK_PORT", "8000")),
        )

    def require_mongodb_uri(self) -> str:
        if not self.mongodb_uri:
            raise RuntimeError(
                "MONGODB_URI is not configured. Copy .env.example to .env or export it."
            )
        return self.mongodb_uri
