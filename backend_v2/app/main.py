from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine, SessionLocal
from app.models import *  # noqa: F401
from app.seed.seed_data import seed

from app.routers.client_router import router as client_router
from app.routers.account_router import router as account_router
from app.routers.transaction_router import router as transaction_router
from app.routers.kyc_flag_router import router as kyc_flag_router
from app.routers.scv_router import router as scv_router
from app.routers.ingestion_router import router as ingestion_router
from app.atlas.routes import router as atlas_router
from app.routers.missioncontrol_runner import router as missioncontrol_router

app = FastAPI(title="Single Client View Backend (Postgres-ready)")

app.include_router(atlas_router)

app.include_router(missioncontrol_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(client_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(kyc_flag_router)
app.include_router(scv_router)
app.include_router(ingestion_router)

