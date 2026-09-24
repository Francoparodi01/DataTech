from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import BulkWriteError

from datatech.domain.models import ProductSnapshot


class MongoSnapshotRepository:
    def __init__(self, uri: str, database: str = "datatech") -> None:
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[database]
        self.collection = self.db["product_snapshots"]

    def ping(self) -> bool:
        self.client.admin.command("ping")
        return True

    def ensure_indexes(self) -> None:
        self.collection.create_index(
            [("source", ASCENDING), ("source_product_id", ASCENDING), ("captured_at", DESCENDING)],
            name="product_history",
        )
        self.collection.create_index(
            [("captured_at", DESCENDING)],
            name="captured_at_desc",
        )
        self.collection.create_index(
            [("normalized_title", "text")],
            name="title_text",
        )

    def insert_snapshots(self, snapshots: Iterable[ProductSnapshot]) -> int:
        documents = [snapshot.to_document() for snapshot in snapshots]
        if not documents:
            return 0
        try:
            result = self.collection.insert_many(documents, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as exc:
            return int(exc.details.get("nInserted", 0))

    def history(
        self,
        source: str,
        product_id: str,
        *,
        since: datetime | None = None,
        limit: int = 500,
    ) -> list[ProductSnapshot]:
        query: dict = {"source": source, "source_product_id": product_id}
        if since is not None:
            query["captured_at"] = {"$gte": since}
        cursor = self.collection.find(query).sort("captured_at", ASCENDING).limit(limit)
        return [ProductSnapshot.from_document(document) for document in cursor]

    def latest_products(self, *, source: str | None = None, limit: int = 100) -> list[dict]:
        match = {"source": source} if source else {}
        pipeline = [
            {"$match": match},
            {"$sort": {"captured_at": -1}},
            {
                "$group": {
                    "_id": {"source": "$source", "source_product_id": "$source_product_id"},
                    "doc": {"$first": "$$ROOT"},
                }
            },
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$sort": {"captured_at": -1}},
            {"$limit": max(1, min(limit, 500))},
            {"$project": {"_id": 0}},
        ]
        return list(self.collection.aggregate(pipeline))
