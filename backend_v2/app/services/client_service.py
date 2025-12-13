from sqlalchemy.orm import Session
from app.schemas.client import ClientCreate
from app.repositories.client_repository import ClientRepository


class ClientService:

    @staticmethod
    def create(db: Session, data: ClientCreate):
        return ClientRepository.create(db, data)

    @staticmethod
    def get(db: Session, client_id: int):
        return ClientRepository.get(db, client_id)

    @staticmethod
    def list(db: Session):
        return ClientRepository.list(db)
