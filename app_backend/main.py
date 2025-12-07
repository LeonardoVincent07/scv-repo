import os  # <-- Added the os import

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json

from .db import Base, engine, SessionLocal
from . import models, schemas
from src.services.client_profile.service import ClientProfileService

# Initialise database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Single Client View (SCV) Backend")

# CORS (for frontend dev server access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (React app)
FRONTEND_DIST = "app_frontend/dist"
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_path)

# Serve MissionLog status snapshot JSON file
MISSIONLOG_PUBLIC = "app_frontend/public/missionlog"
if os.path.isdir(MISSIONLOG_PUBLIC):
    app.mount("/missionlog", StaticFiles(directory=MISSIONLOG_PUBLIC), name="missionlog")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

# ------------------------------------
# Load raw records for a client
# ------------------------------------
def _load_raw_records_for_client(db: Session, client_id: str) -> list[dict[str, any]]:
    rows: list[models.SourceRecord] = (
        db.query(models.SourceRecord)
        .filter(models.SourceRecord.client_id == client_id)
        .all()
    )

    records: list[dict[str, any]] = []
    for row in rows:
        try:
            payload = json.loads(row.payload_json)
        except json.JSONDecodeError:
            continue

        if "_source" not in payload:
            payload["_source"] = row.system

        records.append(payload)

    return records

# Endpoint to get client profile
@app.get("/clients/{client_id}/profile", tags=["clients"])
def get_client_profile(client_id: str, db: Session = Depends(get_db)):
    raw_records = _load_raw_records_for_client(db, client_id)

    service = ClientProfileService()
    profile = service.assemble_base_profile(client_id, raw_records)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile could not be assembled")

    return profile

# ------------------------------------
# Endpoint to get client sources
# ------------------------------------
@app.get("/clients/{client_id}/sources", tags=["clients"])
def get_client_sources(client_id: str, db: Session = Depends(get_db)):
    # Query the source records for the given client_id
    rows = db.query(models.SourceRecord).filter(models.SourceRecord.client_id == client_id).all()

    # If no sources found, return an empty list
    if not rows:
        return []

    # Otherwise, return the source records
    return rows




