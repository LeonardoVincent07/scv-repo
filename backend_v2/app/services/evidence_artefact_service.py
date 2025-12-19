# backend_v2/app/services/evidence_artefact_service.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from sqlalchemy import text
from sqlalchemy.orm import Session

_EVIDENCE_ARTEFACTS_COLS: Optional[Set[str]] = None


def _get_evidence_artefacts_columns(db: Session) -> Set[str]:
    global _EVIDENCE_ARTEFACTS_COLS
    if _EVIDENCE_ARTEFACTS_COLS is not None:
        return _EVIDENCE_ARTEFACTS_COLS

    rows = db.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'evidence_artefacts'
        """)
    ).fetchall()

    _EVIDENCE_ARTEFACTS_COLS = {r[0] for r in rows}
    return _EVIDENCE_ARTEFACTS_COLS


class EvidenceArtefactService:
    @staticmethod
    def list_by_client(db: Session, client_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Return evidence artefacts linked to a client.

        Current DB shape (per your table):
          evidence_artefacts(artefact_id, evidence_bundle_id, artefact_type, created_at, content jsonb)

        There is no direct client_id, so we link via:
          match_decisions(matched_client_id) -> source_record_id
          evidence_artefacts.content->'source_record_ids' contains those IDs
        """
        cols = _get_evidence_artefacts_columns(db)

        # 1) Pull the client's source_record_ids from match_decisions
        src_rows = db.execute(
            text("""
                SELECT DISTINCT source_record_id::text AS source_record_id
                FROM match_decisions
                WHERE matched_client_id = :client_id
            """),
            {"client_id": client_id},
        ).fetchall()

        source_ids = [r[0] for r in src_rows if r and r[0]]
        if not source_ids:
            return []

        # 2) Select artefacts; adapt to schema if columns vary slightly
        select_parts = [
            "artefact_id",
            "evidence_bundle_id",
            "artefact_type",
            "created_at",
            "content",
        ]

        # If some environments use artifact_* spelling, adapt (defensive)
        if "artefact_id" not in cols and "artifact_id" in cols:
            select_parts[0] = "artifact_id AS artefact_id"
        if "evidence_bundle_id" not in cols and "bundle_id" in cols:
            select_parts[1] = "bundle_id AS evidence_bundle_id"
        if "artefact_type" not in cols and "artifact_type" in cols:
            select_parts[2] = "artifact_type AS artefact_type"

        # Filter: jsonb array contains-any using ?| against text[]
        sql = f"""
            SELECT {", ".join(select_parts)}
            FROM evidence_artefacts
            WHERE (content -> 'source_record_ids') ?| :source_ids
            ORDER BY created_at DESC
            LIMIT :limit
        """

        rows = db.execute(
            text(sql),
            {
                "source_ids": source_ids,  # SQLAlchemy/psycopg will bind Python list as text[]
                "limit": limit,
            },
        ).fetchall()

        artefacts: List[Dict[str, Any]] = []
        for r in rows:
            d = dict(r._mapping)

            # Shape to what the UI panel expects (keep existing keys too)
            # UI-friendly fields:
            d["source_system"] = "MATCHING"  # stable label; can refine later
            d["storage_ref"] = str(d.get("evidence_bundle_id") or d.get("artefact_id"))
            artefacts.append(d)

        return artefacts


