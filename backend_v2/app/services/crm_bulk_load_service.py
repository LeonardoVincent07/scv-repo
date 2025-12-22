from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, Protocol

from sqlalchemy.orm import Session

from app.repositories.crm_contact_repository import CRMContactRepository


@dataclass(frozen=True)
class IngestionResult:
    total: int
    inserted: int
    updated: int
    skipped: int


class CrmSource(Protocol):
    def read(self) -> Iterable[Dict[str, Optional[str]]]:
        """
        Each record must at minimum supply:
          - source_system
          - source_record_id
        Other fields are optional.
        """
        ...


class FileCrmSource:
    """
    Deterministic, controlled source for ST-05.
    CSV header must include:
      source_system, source_record_id, first_name, last_name, email
    """
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> Iterator[Dict[str, Optional[str]]]:
        with self.path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalise keys we care about (ignore extras)
                yield {
                    "source_system": (row.get("source_system") or "").strip() or None,
                    "source_record_id": (row.get("source_record_id") or "").strip() or None,
                    "first_name": (row.get("first_name") or "").strip() or None,
                    "last_name": (row.get("last_name") or "").strip() or None,
                    "email": (row.get("email") or "").strip() or None,
                }


class BulkCrmIngestionService:
    """
    ST-05 operational batch ingestion.
    - minimal validation
    - real persistence through repository
    - idempotent via upsert
    """

    @staticmethod
    def ingest(db: Session, source: CrmSource) -> IngestionResult:
        total = inserted = updated = skipped = 0

        for rec in source.read():
            total += 1

            source_system = rec.get("source_system")
            source_record_id = rec.get("source_record_id")

            # Minimal required-field validation only (strict scope)
            if not source_system or not source_record_id:
                skipped += 1
                continue

            status, _row = CRMContactRepository.upsert(
                db,
                source_system=source_system,
                source_record_id=source_record_id,
                first_name=rec.get("first_name"),
                last_name=rec.get("last_name"),
                email=rec.get("email"),
            )

            if status == "inserted":
                inserted += 1
            else:
                updated += 1

        db.commit()

        return IngestionResult(
            total=total,
            inserted=inserted,
            updated=updated,
            skipped=skipped,
        )
