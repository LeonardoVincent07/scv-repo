from typing import List, Dict, Any
import datetime

class AuditIngestionService:
    """
    Service for auditing ingestion events (ST-30).
    Records audit entries for each ingestion event.
    """
    def __init__(self):
        # In-memory audit log for demonstration; replace with persistent storage in production
        self._audit_log: List[Dict[str, Any]] = []

    def record_audit_entry(self, source: str, entity_id: str, status: str, details: Dict[str, Any] = None) -> None:
        """
        Record an audit entry for an ingestion event.
        :param source: Source system name (e.g., 'CRM', 'KYC')
        :param entity_id: The ID of the ingested entity (e.g., client_id)
        :param status: Status of the ingestion (e.g., 'success', 'fail')
        :param details: Optional additional details (dict)
        """
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
            "source": source,
            "entity_id": entity_id,
            "status": status,
            "details": details or {}
        }
        self._audit_log.append(entry)

    def get_audit_entries(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit entries, optionally filtered by entity_id.
        :param entity_id: If provided, only entries for this entity are returned.
        :return: List of audit entries (dicts)
        """
        if entity_id:
            return [entry for entry in self._audit_log if entry["entity_id"] == entity_id]
        return list(self._audit_log)
