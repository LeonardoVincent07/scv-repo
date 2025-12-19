from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from sqlalchemy import text
from sqlalchemy.orm import Session


# Cache discovered columns so we don't hit information_schema on every request
_MATCH_DECISIONS_COLS: Optional[Set[str]] = None


def _get_match_decisions_columns(db: Session) -> Set[str]:
    global _MATCH_DECISIONS_COLS
    if _MATCH_DECISIONS_COLS is not None:
        return _MATCH_DECISIONS_COLS

    rows = db.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'match_decisions'
        """)
    ).fetchall()

    _MATCH_DECISIONS_COLS = {r[0] for r in rows}
    return _MATCH_DECISIONS_COLS


class MatchDecisionService:
    @staticmethod
    def list_by_client(db: Session, client_id: int, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Return match decisions for a client, newest first.

        Important:
        - Uses information_schema to adapt to whether optional columns exist
          (e.g. source_system/system, confidence).
        - Returns dict rows to keep profile contract flexible (matches current SCV pattern).
        """
        cols = _get_match_decisions_columns(db)

        # Core columns (assumed present from your schema)
        select_parts = [
            "match_decision_id",
            "match_run_id",
            "source_record_id",
            "decided_at",
            "decision",
            "matched_client_id",
        ]

        # Optional columns used by the UI
        if "source_system" in cols:
            select_parts.append("source_system")
        elif "system" in cols:
            select_parts.append("system AS source_system")
        else:
            select_parts.append("NULL AS source_system")

        if "confidence" in cols:
            select_parts.append("confidence")
        else:
            select_parts.append("NULL AS confidence")

        # Keep any extra useful columns if they exist (won't break UI; expand panel will show them)
        for extra in ["details", "reason", "rule", "candidate_id"]:
            if extra in cols:
                select_parts.append(extra)

        sql = f"""
            SELECT {", ".join(select_parts)}
            FROM match_decisions
            WHERE matched_client_id = :client_id
            ORDER BY decided_at DESC
            LIMIT :limit
        """

        rows = db.execute(text(sql), {"client_id": client_id, "limit": limit}).fetchall()
        return [dict(r._mapping) for r in rows]
