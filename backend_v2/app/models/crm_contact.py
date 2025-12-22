from __future__ import annotations

import uuid
from sqlalchemy import Column, DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


class CRMContact(Base):
    """
    ST-05 owned persistence table for CRM bulk ingestion.

    Idempotency is enforced via UNIQUE(source_system, source_record_id).
    """
    __tablename__ = "crm_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_system = Column(String, nullable=False)
    source_record_id = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("source_system", "source_record_id", name="uq_crm_contacts_source_key"),
    )
