from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.client_service import ClientService
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.services.kyc_flag_service import KycFlagService


router = APIRouter(prefix="/scv", tags=["single_client_view"])


@router.get("/{client_id}")
def get_single_client_view(client_id: int, db: Session = Depends(get_db)):
    client = ClientService.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    accounts = AccountService.list_by_client(db, client_id)
    account_ids = [a.id for a in accounts]
    transactions_by_account = {
        acc_id: TransactionService.list_by_account(db, acc_id) for acc_id in account_ids
    }
    kyc_flags = KycFlagService.list_by_client(db, client_id)

    return {
        "client": client,
        "accounts": accounts,
        "transactions_by_account": transactions_by_account,
        "kyc_flags": kyc_flags,
    }
