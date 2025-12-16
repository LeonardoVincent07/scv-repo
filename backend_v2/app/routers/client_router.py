from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.client import ClientCreate, ClientRead
from app.schemas.account import AccountRead
from app.schemas.kyc_flag import KycFlagRead
from app.services.client_service import ClientService
from app.services.account_service import AccountService
from app.services.kyc_flag_service import KycFlagService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/clients", tags=["clients"])


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


@router.get("/{client_id}/kyc-flags", response_model=list[KycFlagRead])
def get_client_kyc_flags(client_id: int, db: Session = Depends(get_db)):
    return KycFlagService.list_by_client(db, client_id)


# -----------------------------------------
# Compatibility endpoints for existing UI
# -----------------------------------------
# App.jsx currently calls:
#   GET /clients/{client_id}/profile
#   GET /clients/{client_id}/sources
# We implement lightweight versions of those
# backed by the new Postgres models.
#
# Canonical contract requirement (SCV_CANONICAL_STATE.md):
# Must return keys (present even if empty):
#   client, accounts, match_decisions, trade_history, audit_trail,
#   regulatory_enrichment, evidence_artefacts


@router.get("/{client_id}/profile")
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
            amt = t.amount
            # Map "transaction" -> UI "trade-like" row (minimal, but real)
            trade_history.append(
                {
                    "trade_id": t.id,
                    "account_id": t.account_id,
                    "trade_date": td,
                    "value_date": t.value_date,
                    "asset_class": "CASH",
                    "instrument": t.currency,  # UI reads instrument/symbol/ccy_pair
                    "direction": "BUY" if (amt is not None and amt >= 0) else "SELL",
                    "quantity": abs(amt) if amt is not None else None,  # UI reads quantity/qty/notional
                    "price": None,
                    "pnl": None,
                    # Keep raw fields for the expandable JSON view
                    "amount": t.amount,
                    "currency": t.currency,
                    "txn_type": t.txn_type,
                    "description": t.description,
                }
            )

    # Canonical keys (always present)
    client_payload = jsonable_encoder(client)
    accounts_payload = jsonable_encoder(accounts)

    # Also keep legacy top-level fields that the existing UI header reads
    profile = {
        # ---- legacy/top-level (do not remove) ----
        "client_id": str(client.id),
        "name": client.full_name,
        "email": client.email,
        "phone": client.phone,
        "country": client.country,
        "segment": client.segment,
        "risk_rating": client.risk_rating,
        "addresses": [],
        "operational_state": {
            "status": "ACTIVE",
            "as_of": None,
            "processing_stage": "PROFILE_COMPOSED",
            "message": "Composed via backend_v2 /clients/{id}/profile",
            "details": {},
        },
        # ---- canonical contract keys (must exist) ----
        "client": client_payload,
        "accounts": accounts_payload,
        "match_decisions": [],
        "trade_history": trade_history,
        "audit_trail": [],
        "regulatory_enrichment": {},
        "evidence_artefacts": [],
    }

    # Map the primary_address into a single address entry if present
    if client.primary_address:
        profile["addresses"].append(
            {
                "line1": client.primary_address,
                "line2": None,
                "city": None,
                "postcode": None,
                "country": client.country,
                "source": "SCV_DB",
            }
        )

    return profile


@router.get("/{client_id}/sources")
def get_client_sources_for_ui(client_id: int, db: Session = Depends(get_db)):
    """
    Return a synthetic 'raw sources' array so the existing UI can render
    something in the Raw sources panel.

    Shape:
      [
        {
          "id": "SCV-<client_id>",
          "system": "SCV_DB",
          "client_id": "<client_id>",
          "payload": { . }
        }
      ]
    """
    client = ClientService.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    accounts = AccountService.list_by_client(db, client_id)
    kyc_flags = KycFlagService.list_by_client(db, client_id)

    payload = {
        "client": {
            "id": client.id,
            "external_id": client.external_id,
            "full_name": client.full_name,
            "email": client.email,
            "phone": client.phone,
            "primary_address": client.primary_address,
            "country": client.country,
            "segment": client.segment,
            "tax_id": client.tax_id,
            "risk_rating": client.risk_rating,
        },
        "accounts": [
            {
                "id": a.id,
                "account_number": a.account_number,
                "account_type": a.account_type,
                "currency": a.currency,
                "status": a.status,
            }
            for a in accounts
        ],
        "kyc_flags": [
            {
                "id": f.id,
                "code": f.code,
                "status": f.status,
                "description": f.description,
                "created_at": f.created_at,
                "resolved_at": f.resolved_at,
            }
            for f in kyc_flags
        ],
    }

    return [
        {
            "id": f"SCV-{client.id}",
            "system": "SCV_DB",
            "client_id": str(client.id),
            "payload": payload,
        }
    ]


