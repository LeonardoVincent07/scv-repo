from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.account import AccountCreate, AccountRead
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionRead


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountRead)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    return AccountService.create(db, data)


@router.get("/{account_id}", response_model=AccountRead | None)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return AccountService.get(db, account_id)


@router.get("/{account_id}/transactions", response_model=list[TransactionRead])
def get_account_transactions(account_id: int, db: Session = Depends(get_db)):
    return TransactionService.list_by_account(db, account_id)
