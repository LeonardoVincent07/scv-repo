from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.crm_contact import CRMContact


class CRMContactRepository:
    @staticmethod
    def upsert(
        db: Session,
        *,
        source_system: str,
        source_record_id: str,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> Tuple[str, CRMContact]:
        """
        Idempotent upsert:
        - Inserts when (source_system, source_record_id) is new
        - Updates mutable fields when it already exists

        Returns: ("inserted" | "updated", row)
        """
        stmt = insert(CRMContact).values(
            source_system=source_system,
            source_record_id=source_record_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        # Update on conflict
        update_cols = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "updated_at": func.now(),
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[CRMContact.source_system, CRMContact.source_record_id],
            set_=update_cols,
        ).returning(CRMContact)

        row = db.execute(stmt).scalar_one()

        # Determine inserted vs updated in a Postgres-friendly way:
        # If created_at == updated_at (fresh insert), treat as inserted.
        # If updated_at moved, treat as updated.
        # Note: created_at/updated_at are server-side; refresh to ensure values.
        db.flush()
        db.refresh(row)

        status = "inserted" if row.created_at == row.updated_at else "updated"
        return status, row
