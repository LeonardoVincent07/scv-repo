from sqlalchemy.orm import Session
from app.schemas.kyc_flag import KycFlagCreate
from app.repositories.kyc_flag_repository import KycFlagRepository


class KycFlagService:

    @staticmethod
    def create(db: Session, data: KycFlagCreate):
        return KycFlagRepository.create(db, data)

    @staticmethod
    def list_by_client(db: Session, client_id: int):
        return KycFlagRepository.list_by_client(db, client_id)
