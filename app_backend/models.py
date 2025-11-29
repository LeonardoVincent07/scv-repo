from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from .db import Base


class SourceRecord(Base):
    """
    Raw upstream record from a given system for a given client_id.

    These rows replace the hard-coded _mock_crm_source/_mock_kyc_source
    in ClientProfileService. We load them, decode the JSON payloads,
    and pass them into assemble_base_profile.
    """
    __tablename__ = "source_records"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True, nullable=False)
    system = Column(String, index=True, nullable=False)  # e.g. "CRM", "KYC"
    payload_json = Column(Text, nullable=False)          # JSON-encoded dict

    __table_args__ = (
        UniqueConstraint("client_id", "system", name="uq_client_system"),
    )
