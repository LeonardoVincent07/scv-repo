import pytest
from src.services.audit.service import AuditIngestionService

def test_record_audit_entry():
    service = AuditIngestionService()
    service.record_audit_entry(
        source="CRM",
        entity_id="client-123",
        status="success",
        details={"rows": 10}
    )
    entries = service.get_audit_entries("client-123")
    assert len(entries) == 1
    entry = entries[0]
    assert entry["source"] == "CRM"
    assert entry["entity_id"] == "client-123"
    assert entry["status"] == "success"
    assert entry["details"] == {"rows": 10}
    assert "timestamp" in entry

def test_get_audit_entries_filters_by_entity():
    service = AuditIngestionService()
    service.record_audit_entry("CRM", "client-1", "success")
    service.record_audit_entry("KYC", "client-2", "fail")
    entries = service.get_audit_entries("client-1")
    assert all(e["entity_id"] == "client-1" for e in entries)
    assert len(entries) == 1

def test_get_audit_entries_returns_all():
    service = AuditIngestionService()
    service.record_audit_entry("CRM", "client-1", "success")
    service.record_audit_entry("KYC", "client-2", "fail")
    entries = service.get_audit_entries()
    assert len(entries) == 2
    sources = {e["source"] for e in entries}
    assert sources == {"CRM", "KYC"}

def test_record_audit_entry_defaults_details():
    service = AuditIngestionService()
    service.record_audit_entry("CRM", "client-3", "success")
    entry = service.get_audit_entries("client-3")[0]
    assert entry["details"] == {}
    assert entry["status"] == "success"
