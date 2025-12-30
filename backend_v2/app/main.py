from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers.client_router import router as client_router
from app.routers.ingestion_router import router as ingestion_router
from app.routers.missioncontrol_runner import router as missioncontrol_router


app = FastAPI(
    title="M7 Single Client View API",
    version="0.1.0",
)

# CORS (unchanged)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (unchanged)
app.include_router(client_router)
app.include_router(ingestion_router)
app.include_router(missioncontrol_router)


# -------------------------------------------------------------------
# Static MissionLog mount (REQUIRED FOR DEMO CAPABILITIES)
# -------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
MISSIONLOG_DIR = REPO_ROOT / "app_frontend" / "public" / "missionlog"

app.mount(
    "/missionlog",
    StaticFiles(directory=str(MISSIONLOG_DIR)),
    name="missionlog",
)

# Health check (unchanged)
@app.get("/health")
def health():
    return {"status": "ok"}

