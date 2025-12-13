from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate


class ClientRepository:

    @staticmethod
    def create(db: Session, data: ClientCreate) -> Client:
        client = Client(**data.model_dump())
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def get(db: Session, client_id: int) -> Client | None:
        return db.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def list(db: Session) -> list[Client]:
        return db.query(Client).all()
