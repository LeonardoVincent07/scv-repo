from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True, nullable=False)
    trade_date = Column(String, nullable=True)
    value_date = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="GBP")
    txn_type = Column(String, nullable=False)  # CREDIT, DEBIT, TRADE, FEE
    description = Column(String, nullable=True)

    account = relationship("Account", backref="transactions")
