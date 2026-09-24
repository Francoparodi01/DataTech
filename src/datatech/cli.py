from __future__ import annotations

import argparse
import json
from collections.abc import Iterable

from datatech.collectors.amazon import AmazonHtmlCollector
from datatech.collectors.mercadolibre import MercadoLibreCollector
from datatech.config import Settings
from datatech.domain.models import ProductSnapshot
from datatech.services.ingestion import IngestionService
from datatech.storage.mongo import MongoSnapshotRepository
from datatech.web.app import create_app


def _emit(snapshots: Iterable[ProductSnapshot]) -> None:
    for snapshot in snapshots:
        document = snapshot.to_document()
        document["captured_at"] = snapshot.captured_at.isoformat()
        print(json.dumps(document, ensure_ascii=False))


def _persist(settings: Settings, snapshots: list[ProductSnapshot]) -> int:
    repository = MongoSnapshotRepository(settings.require_mongodb_uri(), settings.mongodb_database)
    return IngestionService(repository).ingest(snapshots)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="datatech")
    sub = parser.add_subparsers(dest="command", required=True)

    meli = sub.add_parser("collect-meli", help="Collect Mercado Libre search results")
    meli.add_argument("--query", required=True)
    meli.add_argument("--site", default="MLA")
    meli.add_argument("--pages", type=int, default=1)
    meli.add_argument("--dry-run", action="store_true")

    amazon = sub.add_parser("collect-amazon", help="Collect Amazon HTML search results")
    amazon.add_argument("--query", required=True)
    amazon.add_argument("--pages", type=int, default=1)
    amazon.add_argument("--marketplace", default="https://www.amazon.com")
    amazon.add_argument("--currency", default="USD")
    amazon.add_argument("--dry-run", action="store_true")

    sub.add_parser("serve", help="Run the development Flask server")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()

    if args.command == "collect-meli":
        collector = MercadoLibreCollector(
            site_id=args.site,
            timeout=settings.request_timeout,
            user_agent=settings.user_agent,
        )
        snapshots = collector.search(args.query, max_pages=args.pages)
        if args.dry_run:
            _emit(snapshots)
        else:
            print(f"inserted={_persist(settings, snapshots)} collected={len(snapshots)}")
        return

    if args.command == "collect-amazon":
        collector = AmazonHtmlCollector(
            marketplace=args.marketplace,
            currency=args.currency,
            timeout=settings.request_timeout,
            user_agent=settings.user_agent,
        )
        snapshots = collector.search(args.query, max_pages=args.pages)
        if args.dry_run:
            _emit(snapshots)
        else:
            print(f"inserted={_persist(settings, snapshots)} collected={len(snapshots)}")
        return

    if args.command == "serve":
        app = create_app(settings)
        app.run(host=settings.flask_host, port=settings.flask_port, debug=False)
