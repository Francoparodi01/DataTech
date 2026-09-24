from __future__ import annotations

from collections.abc import Iterable

from datatech.domain.models import ProductSnapshot
from datatech.storage.mongo import MongoSnapshotRepository


class IngestionService:
    def __init__(self, repository: MongoSnapshotRepository) -> None:
        self.repository = repository

    def ingest(self, snapshots: Iterable[ProductSnapshot]) -> int:
        snapshots = list(snapshots)
        self.repository.ensure_indexes()
        return self.repository.insert_snapshots(snapshots)
