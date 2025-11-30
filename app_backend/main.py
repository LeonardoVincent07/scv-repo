# Story: ST-00-backend-api-availability
# Feature: FT-00-backend-fundamentals
# Epic: E00
# Purpose: Backend bootstrapping and health endpoint.

from typing import Any, Dict, List
import json
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from . import models, schemas

# Import your existing SCV domain service
from src.services.client_profile.service import ClientProfileService

# ------------------------------------
# Initialise database
# ------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Single Client View (SCV) Backend")

# ------------------------------------
# CORS (kept for optional Vite dev server use)
# ------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------
# Serve built frontend (Vite dist)
# ------------------------------------
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app_frontend", "dist")
)

if os.path.isdir(FRONTEND_DIST):
    # Serve static assets (JS/CSS, etc.)
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    async def serve_react_index():
        """Serve the built React single-page app."""
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_path)


# ------------------------------------
# DB session dependency
# ------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------
# Load raw records for a client
# ------------------------------------
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
            continue

        if "_source" not in payload:
            payload["_source"] = row.system

        records.append(payload)

    return records


# ------------------------------------
# Health check
# ------------------------------------
@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# ------------------------------------
# Ingestion endpoint
# ------------------------------------
@app.post("/ingest", response_model=schemas.SourceRecordRead, tags=["ingestion"])
def ingest_source_record(
    record_in: schemas.SourceRecordCreate,
    db: Session = Depends(get_db),
):
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


# ------------------------------------
# List raw source records
# ------------------------------------
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


# ------------------------------------
# SCV Profile endpoint (LDM aligned)
# ------------------------------------
@app.get("/clients/{client_id}/profile", tags=["clients"])
def get_client_profile(
    client_id: str,
    db: Session = Depends(get_db),
):
    raw_records = _load_raw_records_for_client(db, client_id)

    service = ClientProfileService()
    profile = service.assemble_base_profile(client_id, raw_records)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile could not be assembled")

    return profile

