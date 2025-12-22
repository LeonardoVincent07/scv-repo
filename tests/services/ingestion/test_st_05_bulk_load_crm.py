from __future__ import annotations

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.crm_bulk_load_service import BulkCrmIngestionService, FileCrmSource


STORY_ID = "ST-05"


def _fixture_path() -> Path:
    return Path("backend_v2/app/fixtures/st05/crm_sample.csv")


def _count_rows(db: Session) -> int:
    return int(db.execute(text("SELECT COUNT(*) FROM crm_contacts")).scalar_one())


def test_bulk_load_persists_records_and_is_idempotent(db_schema_session: Session):
    db = db_schema_session

    # 1) Initial load
    result_1 = BulkCrmIngestionService.ingest(db, FileCrmSource(_fixture_path()))
    count_1 = _count_rows(db)

    assert result_1.total == 3
    assert result_1.skipped == 0
    assert result_1.inserted == 3
    assert result_1.updated == 0
    assert count_1 == 3

    # 2) Re-run (must not duplicate, must upsert)
    result_2 = BulkCrmIngestionService.ingest(db, FileCrmSource(_fixture_path()))
    count_2 = _count_rows(db)

    assert result_2.total == 3
    assert result_2.skipped == 0
    assert result_2.inserted == 0
    assert result_2.updated == 3
    assert count_2 == 3

   
