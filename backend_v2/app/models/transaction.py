from sqlalchemy import Column, Integer, String, Date, Float
from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, nullable=False)

    trade_date = Column(Date, nullable=True)
    value_date = Column(Date, nullable=True)

    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)

    txn_type = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # --- Added to match DB schema ---
    price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
