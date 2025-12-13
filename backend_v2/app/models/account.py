from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True, nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, nullable=True)   # e.g. CASH, SECURITIES, MARGIN
    currency = Column(String, nullable=False, default="GBP")
    status = Column(String, nullable=False, default="OPEN")  # OPEN, CLOSED
    opened_at = Column(String, nullable=True)
    closed_at = Column(String, nullable=True)

    client = relationship("Client", backref="accounts")
