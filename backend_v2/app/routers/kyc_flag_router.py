from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.kyc_flag import KycFlagCreate, KycFlagRead
from app.services.kyc_flag_service import KycFlagService


router = APIRouter(prefix="/kyc-flags", tags=["kyc_flags"])


@router.post("/", response_model=KycFlagRead)
def create_kyc_flag(data: KycFlagCreate, db: Session = Depends(get_db)):
    return KycFlagService.create(db, data)
