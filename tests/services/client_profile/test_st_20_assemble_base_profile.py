import pytest
from src.services.client_profile.service import ClientProfileService

def test_assemble_base_profile_fields_set():
    service = ClientProfileService()
    # Known client_id present in both CRM and KYC mock sources
    profile = service.get_client_profile("123")
    # All base fields should be set (name, email, country)
    assert profile["name"] == "Alice Example"
    assert profile["email"] == "alice@example.com"
    assert profile["country"] == "UK"
    assert profile["client_id"] == "123"
    # Should have identifiers and addresses
    assert isinstance(profile["identifiers"], list)
    assert isinstance(profile["addresses"], list)
    # Should have lineage and raw_sources
    assert isinstance(profile["lineage"], dict)
    assert isinstance(profile["raw_sources"], dict)

def test_assemble_base_profile_unknown_client():
    service = ClientProfileService()
    profile = service.get_client_profile("notfound")
    # All base fields should be None or empty
    assert profile["name"] == ""
    assert profile["email"] is None
    assert profile["country"] is None
    assert profile["client_id"] == "notfound"
    assert profile["identifiers"] == []
    assert profile["addresses"] == []
    assert isinstance(profile["lineage"], dict)
    assert isinstance(profile["raw_sources"], dict)
