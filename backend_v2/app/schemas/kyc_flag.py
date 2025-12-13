from pydantic import BaseModel


class KycFlagBase(BaseModel):
    client_id: int
    code: str
    description: str | None = None
    status: str = "OPEN"
    created_at: str | None = None
    resolved_at: str | None = None


class KycFlagCreate(KycFlagBase):
    pass


class KycFlagRead(KycFlagBase):
    id: int

    class Config:
        from_attributes = True
