from typing import Any, Dict, List
import json

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from . import models, schemas

# Import your existing SCV domain service
from src.services.client_profile.service import ClientProfileService


# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Single Client View (SCV) Backend")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Internal helper
# -----------------------------
def _load_raw_records_for_client(db: Session, client_id: str) -> List[Dict[str, Any]]:
    rows: List[models.SourceRecord] = (
        db.query(models.SourceRecord)
        .filter(models.SourceRecord.client_id == client_id)
        .all()
    )

    records: List[Dict[str, Any]] = []
    for row in rows:
        try:
            payload = json.loads(row.payload_json)
        except json.JSONDecodeError:
            # In MVP, silently skip corrupt rows
            continue

        # Ensure _source is present (ClientProfileService expects this)
        if "_source" not in payload:
            payload["_source"] = row.system

        records.append(payload)

    return records


# -----------------------------
# System endpoints
# -----------------------------
@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# -----------------------------
# Ingestion endpoints
# -----------------------------
@app.post("/ingest", response_model=schemas.SourceRecordRead, tags=["ingestion"])
def ingest_source_record(
    record_in: schemas.SourceRecordCreate,
    db: Session = Depends(get_db),
):
    """
    Store or update a raw upstream record for (client_id, system).

    Example payload for CRM:
    {
      "client_id": "123",
      "system": "CRM",
      "payload": {
        "identifier": "crm-123",
        "name": "Alice Example",
        "email": "alice@example.com",
        "country": "UK",
        "address": {
          "line1": "1 Main St",
          "city": "London",
          "postcode": "E1 1AA",
          "country": "UK"
        }
      }
    }
    """
    existing = (
        db.query(models.SourceRecord)
        .filter(
            models.SourceRecord.client_id == record_in.client_id,
            models.SourceRecord.system == record_in.system,
        )
        .one_or_none()
    )

    payload_json = json.dumps(record_in.payload)

    if existing:
        existing.payload_json = payload_json
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    row = models.SourceRecord(
        client_id=record_in.client_id,
        system=record_in.system,
        payload_json=payload_json,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get(
    "/clients/{client_id}/sources",
    response_model=list[schemas.SourceRecordRead],
    tags=["clients"],
)
def list_client_sources(
    client_id: str,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.SourceRecord)
        .filter(models.SourceRecord.client_id == client_id)
        .all()
    )
    out: List[schemas.SourceRecordRead] = []
    for row in rows:
        out.append(
            schemas.SourceRecordRead(
                id=row.id,
                client_id=row.client_id,
                system=row.system,
                payload=json.loads(row.payload_json),
            )
        )
    return out


# -----------------------------
# SCV profile endpoint (LDM aligned)
# -----------------------------
@app.get("/clients/{client_id}/profile", tags=["clients"])
def get_client_profile(
    client_id: str,
    db: Session = Depends(get_db),
):
    """
    Assemble the canonical SCV ClientProfile for the given client_id,
    using raw source records from the database and the existing
    ClientProfileService. The returned dict matches the ClientProfile LDM.
    """
    raw_records = _load_raw_records_for_client(db, client_id)

    service = ClientProfileService()
    profile = service.assemble_base_profile(client_id, raw_records)

    # profile is a dict derived from ClientProfile:
    # client_id, name, email, country, identifiers, addresses,
    # lineage, quality, metadata, raw_sources, etc.
    if not profile:
        raise HTTPException(status_code=404, detail="Profile could not be assembled")

    return profile
