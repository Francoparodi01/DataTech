from __future__ import annotations

from datetime import UTC, datetime, timedelta

from flask import Flask, jsonify, render_template, request

from datatech.analytics.deals import assess_deal
from datatech.analytics.pricing import summarize_price_history
from datatech.config import Settings
from datatech.storage.mongo import MongoSnapshotRepository


def create_app(
    settings: Settings | None = None,
    repository: MongoSnapshotRepository | None = None,
) -> Flask:
    settings = settings or Settings.from_env()
    app = Flask(__name__)

    if repository is None and settings.mongodb_uri:
        repository = MongoSnapshotRepository(settings.mongodb_uri, settings.mongodb_database)

    @app.get("/health")
    def health():
        if repository is None:
            return jsonify({"status": "degraded", "database": "not_configured"}), 503
        try:
            repository.ping()
            return jsonify({"status": "ok", "database": "ok"})
        except Exception as exc:  # pragma: no cover - depends on external DB
            payload = {"status": "degraded", "database": "unavailable", "error": str(exc)}
            return jsonify(payload), 503

    @app.get("/")
    def dashboard():
        products = repository.latest_products(limit=100) if repository else []
        return render_template(
            "dashboard.html",
            products=products,
            configured=repository is not None,
        )

    @app.get("/api/products")
    def products():
        if repository is None:
            return jsonify({"error": "database_not_configured"}), 503
        source = request.args.get("source") or None
        limit = request.args.get("limit", default=100, type=int)
        rows = repository.latest_products(source=source, limit=limit)
        for row in rows:
            if isinstance(row.get("captured_at"), datetime):
                row["captured_at"] = row["captured_at"].isoformat()
        return jsonify(rows)

    @app.get("/api/deal/<source>/<product_id>")
    def deal(source: str, product_id: str):
        if repository is None:
            return jsonify({"error": "database_not_configured"}), 503
        since = datetime.now(UTC) - timedelta(days=90)
        history = repository.history(source, product_id, since=since)
        if not history:
            return jsonify({"error": "not_found"}), 404
        summary = summarize_price_history(history)
        assessment = assess_deal(summary)
        return jsonify({"summary": summary.to_dict(), "deal": assessment.to_dict()})

    return app
