from sqlalchemy.orm import Session
from app.schemas.account import AccountCreate
from app.repositories.account_repository import AccountRepository


class AccountService:

    @staticmethod
    def create(db: Session, data: AccountCreate):
        return AccountRepository.create(db, data)

    @staticmethod
    def get(db: Session, account_id: int):
        return AccountRepository.get(db, account_id)

    @staticmethod
    def list_by_client(db: Session, client_id: int):
        return AccountRepository.list_by_client(db, client_id)
