from typing import Any, Dict, Optional
from pydantic import BaseModel


class SourceRecordCreate(BaseModel):
    client_id: str
    system: str                   # "CRM", "KYC", "MDM", etc.
    payload: Dict[str, Any]       # raw record from that system


class SourceRecordRead(BaseModel):
    id: int
    client_id: str
    system: str
    payload: Dict[str, Any]

    class Config:
        orm_mode = True
