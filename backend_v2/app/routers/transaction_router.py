from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    return TransactionService.create(db, data)
