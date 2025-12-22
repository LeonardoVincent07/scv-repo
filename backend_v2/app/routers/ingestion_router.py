from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.crm_bulk_load_service import BulkCrmIngestionService, FileCrmSource

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/crm/bulk")
def bulk_load_crm(db: Session = Depends(get_db)):
    """
    ST-05 demo-first endpoint.

    Guarded so it cannot be triggered accidentally in non-demo scenarios.
    Set:
      SCV_DEMO_INGESTION_ENABLED=true
    """
    enabled = os.getenv("SCV_DEMO_INGESTION_ENABLED", "false").lower() == "true"
    if not enabled:
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    fixture_path = Path("backend_v2/app/fixtures/st05/crm_sample.csv")
    if not fixture_path.exists():
        raise HTTPException(status_code=500, detail=f"Fixture not found: {fixture_path}")

    result = BulkCrmIngestionService.ingest(db, FileCrmSource(fixture_path))
    return {
        "total": result.total,
        "inserted": result.inserted,
        "updated": result.updated,
        "skipped": result.skipped,
    }
