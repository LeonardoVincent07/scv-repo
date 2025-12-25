from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.crm_bulk_load_service import (
    BulkCrmIngestionService,
    FileCrmSource,
)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

# Resolve paths relative to this file, not the process working directory
BASE_DIR = Path(__file__).resolve().parents[1]


def _demo_enabled() -> bool:
    return os.getenv("SCV_DEMO_INGESTION_ENABLED", "false").lower() == "true"


@router.post("/crm/bulk")
def bulk_load_crm(db: Session = Depends(get_db)):
    """
    ST-05 demo-first endpoint (original sample fixture).

    Loads crm_sample.csv – DO NOT CHANGE.
    """
    if not _demo_enabled():
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    fixture_path = BASE_DIR / "fixtures" / "st05" / "crm_sample.csv"
    if not fixture_path.exists():
        raise HTTPException(status_code=500, detail=f"Fixture not found: {fixture_path}")

    result = BulkCrmIngestionService.ingest(db, FileCrmSource(fixture_path))
    return {
        "total": result.total,
        "inserted": result.inserted,
        "updated": result.updated,
        "skipped": result.skipped,
    }


@router.post("/crm/bulk_demo_corporate")
def bulk_load_crm_demo_corporate(db: Session = Depends(get_db)):
    """
    Demo-only endpoint that loads corporate-style CRM records.
    """
    if not _demo_enabled():
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    fixture_path = BASE_DIR / "fixtures" / "st05" / "crm_demo_corporate.csv"
    if not fixture_path.exists():
        raise HTTPException(status_code=500, detail=f"Fixture not found: {fixture_path}")

    result = BulkCrmIngestionService.ingest(db, FileCrmSource(fixture_path))
    return {
        "fixture": "crm_demo_corporate.csv",
        "total": result.total,
        "inserted": result.inserted,
        "updated": result.updated,
        "skipped": result.skipped,
    }


@router.get("/crm/contacts")
def list_crm_contacts(
    db: Session = Depends(get_db),
    source_system: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
):
    """
    Demo utility: list ingested CRM contacts (for Pre-Matched Records UI).
    """
    if not _demo_enabled():
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    if source_system:
        rows = (
            db.execute(
                text(
                    """
                    SELECT id, source_system, source_record_id, first_name, last_name, email, created_at, updated_at
                    FROM crm_contacts
                    WHERE source_system = :source_system
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"source_system": source_system, "limit": limit},
            )
            .mappings()
            .all()
        )
    else:
        rows = (
            db.execute(
                text(
                    """
                    SELECT id, source_system, source_record_id, first_name, last_name, email, created_at, updated_at
                    FROM crm_contacts
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            )
            .mappings()
            .all()
        )

    return {"records": [dict(r) for r in rows]}


@router.get("/crm/contacts/count")
def crm_contacts_count(db: Session = Depends(get_db)):
    """
    Demo utility: confirm how many CRM ingestion records exist.
    """
    if not _demo_enabled():
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    count = int(db.execute(text("SELECT COUNT(*) FROM crm_contacts")).scalar_one())
    return {"count": count}


@router.delete("/crm/contacts")
def delete_crm_contacts(
    db: Session = Depends(get_db),
    source_system: str | None = Query(default=None),
):
    """
    Demo utility: delete ingested CRM contacts.

    - If source_system is provided, deletes only those rows
    - If omitted, deletes all rows
    """
    if not _demo_enabled():
        raise HTTPException(status_code=403, detail="Demo ingestion disabled")

    if source_system:
        res = db.execute(
            text("DELETE FROM crm_contacts WHERE source_system = :source_system"),
            {"source_system": source_system},
        )
    else:
        res = db.execute(text("DELETE FROM crm_contacts"))

    db.commit()
    return {
        "deleted": int(res.rowcount or 0),
        "scope": {"source_system": source_system},
    }




