from sqlalchemy.orm import Session
from app.models.kyc_flag import KycFlag
from app.schemas.kyc_flag import KycFlagCreate


class KycFlagRepository:

    @staticmethod
    def create(db: Session, data: KycFlagCreate) -> KycFlag:
        flag = KycFlag(**data.model_dump())
        db.add(flag)
        db.commit()
        db.refresh(flag)
        return flag

    @staticmethod
    def list_by_client(db: Session, client_id: int) -> list[KycFlag]:
        return db.query(KycFlag).filter(KycFlag.client_id == client_id).all()
