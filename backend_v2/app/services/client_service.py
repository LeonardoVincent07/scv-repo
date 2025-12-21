from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.schemas.client import ClientCreate
from app.repositories.client_repository import ClientRepository


class ClientService:
    @staticmethod
    def create(db: Session, data: ClientCreate):
        return ClientRepository.create(db, data)

    @staticmethod
    def list(db: Session):
        return ClientRepository.list(db)

    @staticmethod
    def get_record(db: Session, client_id: int):
        """
        Returns the raw client record from persistence (ORM model or dict),
        without shaping it into the logical data model.
        """
        return ClientRepository.get(db, client_id)

    @staticmethod
    def get(db: Session, client_id: int) -> Optional[Dict[str, Any]]:
        """
        Returns a ClientProfile shaped according to the Initial Logical Data Model (LDM).

        This is a read-only deterministic assembly of core attributes from the persisted
        client record, with empty placeholders for other LDM sections.
        """
        client = ClientRepository.get(db, client_id)
        if client is None:
            return None

        return ClientService._assemble_client_profile(client)

    @staticmethod
    def _assemble_client_profile(client: Any) -> Dict[str, Any]:
        """
        Assemble a ClientProfile structure as per the LDM.

        Populates core attributes where available and provides empty placeholders for:
        identifiers, addresses, lineage, quality, metadata, raw_sources.
        """

        def pick(obj: Any, *names: str) -> Any:
            # Supports ORM objects (attributes) and dict-like records (keys)
            for n in names:
                if isinstance(obj, dict) and n in obj:
                    return obj[n]
                if hasattr(obj, n):
                    return getattr(obj, n)
            return None

        client_id = pick(client, "client_id", "id")
        name = pick(client, "name", "full_name")
        email = pick(client, "email", "primary_email")
        country = pick(client, "country", "country_of_residence")

        # Full LDM shape with empty placeholders
        profile: Dict[str, Any] = {
            "client_id": client_id,
            "name": name,
            "email": email,
            "country": country,
            "identifiers": [],  # type: List[Dict[str, Any]]
            "addresses": [],    # type: List[Dict[str, Any]]
            "lineage": {},      # type: Dict[str, Any]
            "quality": {},      # type: Dict[str, Any]
            "metadata": {},     # type: Dict[str, Any]
            "raw_sources": [],  # type: List[Dict[str, Any]]
        }

        return profile
