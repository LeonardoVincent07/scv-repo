from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


class TransactionRepository:

    @staticmethod
    def create(db: Session, data: TransactionCreate) -> Transaction:
        txn = Transaction(**data.model_dump())
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def list_by_account(db: Session, account_id: int) -> list[Transaction]:
        return db.query(Transaction).filter(Transaction.account_id == account_id).all()
