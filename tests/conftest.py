from __future__ import annotations

import uuid
import pytest
from sqlalchemy import text

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend_v2"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.db import Base, SessionLocal, engine

# Ensure models are imported so Base.metadata knows about them
from app.models import *  # noqa: F401,F403


def _is_postgres() -> bool:
    return engine.url.drivername.startswith("postgresql")


@pytest.fixture(scope="function")
def db_schema_session():
    """
    Real DB session isolated by ephemeral schema.

    - Creates schema scv_st05_<uuid>
    - Sets search_path to that schema on the session connection
    - Creates tables in that schema (using the SAME connection)
    - Drops schema afterwards (disposable)
    """
    if not _is_postgres():
        pytest.fail(f"ST-05 requires Postgres; got driver: {engine.url.drivername}")

    schema = f"scv_st05_{uuid.uuid4().hex}"

    db = SessionLocal()
    try:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
        db.execute(text(f'SET search_path TO "{schema}"'))
        db.commit()

        # IMPORTANT: create tables using the same connection that has search_path set
        conn = db.connection()
        Base.metadata.create_all(bind=conn)

        yield db

    finally:
        try:
            db.rollback()
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            db.commit()
        finally:
            db.close()
