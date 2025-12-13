from sqlalchemy import Column, Integer, String
from app.db import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    primary_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    segment = Column(String, nullable=True)
    risk_rating = Column(String, nullable=True)
