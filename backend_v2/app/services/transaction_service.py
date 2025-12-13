from sqlalchemy.orm import Session
from app.schemas.transaction import TransactionCreate
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:

    @staticmethod
    def create(db: Session, data: TransactionCreate):
        return TransactionRepository.create(db, data)

    @staticmethod
    def list_by_account(db: Session, account_id: int):
        return TransactionRepository.list_by_account(db, account_id)
