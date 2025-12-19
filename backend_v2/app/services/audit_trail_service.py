# backend_v2/app/services/audit_trail_service.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session


# Cache: detect which audit table exists and what columns it has
_AUDIT_TABLE: Optional[str] = None
_AUDIT_COLS: Optional[Set[str]] = None


def _detect_audit_table(db: Session) -> Tuple[Optional[str], Set[str]]:
    """
    Find the audit table in the current DB, and return (table_name, columns).

    We’re defensive because environments can differ slightly.
    """
    global _AUDIT_TABLE, _AUDIT_COLS
    if _AUDIT_TABLE is not None and _AUDIT_COLS is not None:
        return _AUDIT_TABLE, _AUDIT_COLS

    # Candidate names (keep simple and explicit)
    candidates = [
        "audit_events",
        "audit_trail",
        "audit_log",
        "audit_logs",
        "audit_entries",
        "audit_entry",
    ]

    # Identify first table that exists
    row = db.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = ANY(:candidates)
            ORDER BY array_position(:candidates, table_name)
            LIMIT 1
            """
        ),
        {"candidates": candidates},
    ).fetchone()

    if not row:
        _AUDIT_TABLE, _AUDIT_COLS = None, set()
        return _AUDIT_TABLE, _AUDIT_COLS

    table_name = row[0]

    cols_rows = db.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :t
            """
        ),
        {"t": table_name},
    ).fetchall()

    cols = {r[0] for r in cols_rows}

    _AUDIT_TABLE, _AUDIT_COLS = table_name, cols
    return _AUDIT_TABLE, _AUDIT_COLS


class AuditTrailService:
    @staticmethod
    def list_by_client(db: Session, client_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Return audit events linked to a client.

        UI expects an array of objects with (ideally):
          - audit_event_id (or id)
          - occurred_at / timestamp / created_at
          - event_type
          - actor
          - details (json-ish) and/or summary fields

        We support multiple possible table shapes by:
          - detecting the audit table name
          - aliasing common columns into a stable output
          - using the most reliable filter available (client_id, entity_id, or source_record_id linkage)
        """
        table_name, cols = _detect_audit_table(db)
        if not table_name:
            return []

        # -------------------------
        # Column mapping (defensive)
        # -------------------------
        # ID column
        if "audit_event_id" in cols:
            id_expr = "audit_event_id"
        elif "id" in cols:
            id_expr = "id"
        else:
            id_expr = "NULL::text AS audit_event_id"

        # Timestamp column
        if "occurred_at" in cols:
            ts_expr = "occurred_at"
        elif "timestamp" in cols:
            ts_expr = "timestamp"
        elif "created_at" in cols:
            ts_expr = "created_at"
        else:
            ts_expr = "NULL AS occurred_at"

        # Event type
        if "event_type" in cols:
            type_expr = "event_type"
        elif "type" in cols:
            type_expr = "type AS event_type"
        elif "action" in cols:
            type_expr = "action AS event_type"
        else:
            type_expr = "NULL AS event_type"

        # Actor
        if "actor" in cols:
            actor_expr = "actor"
        elif "user" in cols:
            actor_expr = '"user" AS actor'
        elif "created_by" in cols:
            actor_expr = "created_by AS actor"
        else:
            actor_expr = "NULL AS actor"

        # Details payload
        if "details" in cols:
            details_expr = "details"
        elif "content" in cols:
            details_expr = "content AS details"
        elif "payload" in cols:
            details_expr = "payload AS details"
        elif "metadata" in cols:
            details_expr = "metadata AS details"
        else:
            details_expr = "NULL AS details"

        select_parts = [
            f"{id_expr} AS audit_event_id",
            f"{ts_expr} AS occurred_at",
            f"{type_expr}",
            f"{actor_expr}",
            f"{details_expr}",
        ]

        # ---------------------------------------
        # Filtering strategy (best available first)
        # ---------------------------------------
        where_sql = None
        params: Dict[str, Any] = {"client_id": client_id, "limit": limit}

        # 1) Direct client_id column
        if "client_id" in cols:
            where_sql = "client_id = :client_id"

        # 2) matched_client_id column
        elif "matched_client_id" in cols:
            where_sql = "matched_client_id = :client_id"

        # 3) entity_id column (string-based)
        elif "entity_id" in cols:
            # support either "1" or "client:1"
            where_sql = "(entity_id = :client_id_txt OR entity_id = :client_id_key)"
            params["client_id_txt"] = str(client_id)
            params["client_id_key"] = f"client:{client_id}"

        # 4) source_record_id linkage (join via match_decisions)
        elif "source_record_id" in cols:
            where_sql = """
                source_record_id::text IN (
                    SELECT DISTINCT source_record_id::text
                    FROM match_decisions
                    WHERE matched_client_id = :client_id
                )
            """

        # 5) details json contains client_id
        elif "details" in cols:
            # If details is jsonb, this will work; if not, it will likely fail at runtime,
            # so only use it as a last resort.
            where_sql = "(details ->> 'client_id') = :client_id_txt"
            params["client_id_txt"] = str(client_id)

        if not where_sql:
            return []

        sql = f"""
            SELECT {", ".join(select_parts)}
            FROM {table_name}
            WHERE {where_sql}
            ORDER BY {ts_expr} DESC NULLS LAST
            LIMIT :limit
        """

        rows = db.execute(text(sql), params).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            d = dict(r._mapping)

            # Normalise event_type/actor keys if they came through without alias
            # (because some branches use AS; some are direct)
            d.setdefault("event_type", d.get("event_type"))
            d.setdefault("actor", d.get("actor"))

            out.append(d)

        return out
