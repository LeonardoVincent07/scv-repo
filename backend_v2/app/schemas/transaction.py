from pydantic import BaseModel


class TransactionBase(BaseModel):
    account_id: int
    trade_date: str | None = None
    value_date: str | None = None
    amount: float
    currency: str = "GBP"
    txn_type: str
    description: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int

    class Config:
        from_attributes = True
