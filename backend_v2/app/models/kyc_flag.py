from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class KycFlag(Base):
    __tablename__ = "kyc_flags"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True, nullable=False)
    code = Column(String, nullable=False)         # e.g. PEP, SANCTIONS, HIGH_RISK
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="OPEN")  # OPEN, CLOSED
    created_at = Column(String, nullable=True)
    resolved_at = Column(String, nullable=True)

    client = relationship("Client", backref="kyc_flags")
