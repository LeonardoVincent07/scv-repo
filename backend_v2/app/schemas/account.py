from pydantic import BaseModel


class AccountBase(BaseModel):
    client_id: int
    account_number: str
    account_type: str | None = None
    currency: str = "GBP"
    status: str = "OPEN"
    opened_at: str | None = None
    closed_at: str | None = None


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int

    class Config:
        from_attributes = True
