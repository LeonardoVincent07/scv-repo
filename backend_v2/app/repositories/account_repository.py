from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account import AccountCreate


class AccountRepository:

    @staticmethod
    def create(db: Session, data: AccountCreate) -> Account:
        acc = Account(**data.model_dump())
        db.add(acc)
        db.commit()
        db.refresh(acc)
        return acc

    @staticmethod
    def get(db: Session, account_id: int) -> Account | None:
        return db.query(Account).filter(Account.id == account_id).first()

    @staticmethod
    def list_by_client(db: Session, client_id: int) -> list[Account]:
        return db.query(Account).filter(Account.client_id == client_id).all()
