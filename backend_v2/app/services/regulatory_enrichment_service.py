from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

class RegulatoryEnrichmentService:
    @staticmethod
    def get_latest_by_client(db: Session, client_id: int) -> Dict[str, Any]:
        row = db.execute(
            text("""
                SELECT
                    fatca_status,
                    crs_status,
                    onboarding_status,
                    kyc_overall_status,
                    derived_risk_notes,
                    updated_at
                FROM client_regulatory_enrichment
                WHERE client_id = :client_id
                ORDER BY updated_at DESC
                LIMIT 1
            """),
            {"client_id": client_id},
        ).fetchone()

        return dict(row._mapping) if row else {}
