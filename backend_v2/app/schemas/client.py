from pydantic import BaseModel


class ClientBase(BaseModel):
    external_id: str | None = None
    full_name: str
    email: str | None = None
    phone: str | None = None
    primary_address: str | None = None
    country: str | None = None
    tax_id: str | None = None
    segment: str | None = None
    risk_rating: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int

    class Config:
        from_attributes = True
