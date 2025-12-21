from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import date  # <-- ADDED (minimal)

from app.db import get_db
from app.schemas.client import ClientCreate, ClientRead
from app.schemas.account import AccountRead
from app.schemas.kyc_flag import KycFlagRead
from app.schemas.scv_profile import SCVClientProfileResponse  # <-- ADDED (only import)
from app.services.client_service import ClientService
from app.services.account_service import AccountService
from app.services.kyc_flag_service import KycFlagService
from app.services.transaction_service import TransactionService
from app.services.match_decision_service import MatchDecisionService
from app.services.regulatory_enrichment_service import RegulatoryEnrichmentService
from app.services.evidence_artefact_service import EvidenceArtefactService
from app.services.audit_trail_service import AuditTrailService




router = APIRouter(prefix="/clients", tags=["clients"])


def _date_to_iso(value):  # <-- ADDED (minimal helper)
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return value
    return str(value)


# -----------------------------
# Basic CRUD / helper endpoints
# -----------------------------
@router.post("/", response_model=ClientRead)
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    return ClientService.create(db, data)


@router.get("/", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db)):
    return ClientService.list(db)


@router.get("/{client_id}", response_model=ClientRead | None)
def get_client(client_id: int, db: Session = Depends(get_db)):
    return ClientService.get(db, client_id)


@router.get("/{client_id}/accounts", response_model=list[AccountRead])
def get_client_accounts(client_id: int, db: Session = Depends(get_db)):
    return AccountService.list_by_client(db, client_id)


@router.get("/{client_id}/kyc_flags", response_model=list[KycFlagRead])
def get_client_kyc_flags(client_id: int, db: Session = Depends(get_db)):
    return KycFlagService.list_by_client(db, client_id)


# ----------------------------------------
# Canonical SCV Profile endpoint for the UI
# ----------------------------------------
# The existing frontend expects a single profile payload at:
#   GET /clients/{client_id}/profile
#
# In the current SCV frontend, the Detailed Client Profile uses a canonical
# "profile" response with embedded panels. Historically, the frontend called
# separate endpoints per panel, but we now keep this contract stable while
# backed by the new Postgres models.
#
# Canonical contract requirement (SCV_CANONICAL_STATE.md):
# Must return keys (present even if empty):
#   client, accounts, match_decisions, trade_history, audit_trail,
#   regulatory_enrichment, evidence_artefacts


@router.get(
    "/{client_id}/profile",
    response_model=SCVClientProfileResponse  # <-- ADDED (only decorator change)
)
def get_client_profile_for_ui(client_id: int, db: Session = Depends(get_db)):
    """
    Canonical SCV profile endpoint.

    Non-negotiables:
    - backend_v2 is canonical runtime
    - ONE canonical endpoint: GET /clients/{id}/profile
    - Must return keys (present even if empty):
        client, accounts, match_decisions, trade_history, audit_trail,
        regulatory_enrichment, evidence_artefacts

    Story 1 focus:
    - trade_history must show REAL data (sourced from transactions table)
    """
    client = ClientService.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    accounts = AccountService.list_by_client(db, client_id)
    account_ids = [a.id for a in accounts]

    # Pull real transactions and flatten into trade_history
    trade_history: list[dict] = []
    for acc_id in account_ids:
        txns = TransactionService.list_by_account(db, acc_id)
        for t in txns:
            td = t.trade_date
            # UI expects strings in some places; keep simple
            trade_history.append(
                {
                    "trade_id": str(t.id),
                    "account_id": str(t.account_id),
                    "trade_date": _date_to_iso(td),  # <-- CHANGED (only functional change)
                    "instrument": None,
                    "direction": t.txn_type,
                    "quantity": abs(t.amount) if t.amount is not None else None,

                    # ONLY CHANGE (pass through real values from transactions table)
                    "price": t.price,
                    "pnl": t.pnl,

                    "amount": t.amount,
                    "currency": t.currency,
                    "txn_type": t.txn_type,
                    "description": t.description,
                }
            )

    match_decisions = MatchDecisionService.list_by_client(db, client_id)

    regulatory_enrichment = RegulatoryEnrichmentService.get_latest_by_client(db, client_id)

    evidence_artefacts = EvidenceArtefactService.list_by_client(db, client_id)

    audit_trail = AuditTrailService.list_by_client(db, client_id)

    # Canonical keys (always present)
    client_payload = jsonable_encoder(client)
    accounts_payload = jsonable_encoder(accounts)

    # Also keep legacy top-level fields that the existing UI header reads
    profile = {
        "client_id": str(client["client_id"]),
        "name": client.get("name"),
        "email": client.get("email"),
        "phone": None,
        "country": client.get("country"),
        "segment": None,
        "risk_rating": None,
        "addresses": [],
        "operational_state": {
            "status": "ACTIVE",
            "as_of": None,
            "processing_stage": "PROFILE_COMPOSED",
            "message": "Composed via backend_v2 /clients/{id}/profile",
            "details": {},
        },
        "client": client_payload,
        "accounts": accounts_payload,
        "match_decisions": match_decisions,
        "trade_history": trade_history,
        "audit_trail": audit_trail,
        "regulatory_enrichment": jsonable_encoder(regulatory_enrichment),
        "evidence_artefacts": evidence_artefacts,
    }

    # Map the primary_address into a single address entry if present
    if client.get("primary_address"):
        profile["addresses"].append(
            {
                "line1": client.get("primary_address"),
                "line2": None,
                "city": None,
                "postcode": None,
                "country": client.get("country"),
                "source": "SCV_DB",
            }
        )

    return profile


@router.get("/{client_id}/sources")
def get_client_sources_for_ui(client_id: int, db: Session = Depends(get_db)):
    """
    Return a synthetic 'raw sources' array so the existing UI can render
    something in the Raw sources panel.

    This is intentionally a placeholder until ingestion/source-record tables
    are implemented. It is safe and non-invasive.
    """
    client = ClientService.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Minimal source records derived from the canonical client row
    sources = [
        {
            "source_system": "SCV_DB",
            "source_record_id": f"client:{client.get('client_id')}",
            "fields": {
                "name": client.get("name"),
                "email": client.get("email"),
                "phone": None,
                "country": client.get("country"),
                "segment": None,
                "risk_rating": None,
                "primary_address": None,
            },
        }
    ]

    return [
    {
        "id": s["source_record_id"],
        "system": s["source_system"],
        "client_id": str(client.get("client_id")),
        "payload": s["fields"],
    }
    for s in sources
]












