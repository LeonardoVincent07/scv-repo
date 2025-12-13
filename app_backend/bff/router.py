from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import SessionLocal

router = APIRouter(prefix="/bff", tags=["bff"])


@router.get("/clients")
def list_clients():
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    id, external_id, full_name, email, phone,
                    primary_address, country, tax_id, segment,
                    risk_rating
                FROM clients
                ORDER BY id
            """)
        ).fetchall()

        return {"clients": [dict(r._mapping) for r in rows]}
    finally:
        db.close()


@router.get("/clients/{client_id}")
def get_client_detail(client_id: int):
    db = SessionLocal()
    try:
        client = db.execute(
            text("SELECT * FROM clients WHERE id = :id"),
            {"id": client_id},
        ).fetchone()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        accounts = db.execute(
            text("SELECT * FROM accounts WHERE client_id = :id"),
            {"id": client_id},
        ).fetchall()

        operational_state = db.execute(
            text("""
                SELECT *
                FROM client_operational_state
                WHERE client_id = :id
                ORDER BY as_of DESC
                LIMIT 1
            """),
            {"id": client_id},
        ).fetchone()

        match_decisions = db.execute(
            text("""
                SELECT *
                FROM match_decisions
                WHERE matched_client_id = :id
                ORDER BY decided_at DESC
                LIMIT 10
            """),
            {"id": client_id},
        ).fetchall()

        return {
            "client": dict(client._mapping),
            "accounts": [dict(r._mapping) for r in accounts],
            "operational_state": dict(operational_state._mapping) if operational_state else None,
            "recent_match_decisions": [dict(r._mapping) for r in match_decisions],
        }

    finally:
        db.close()
