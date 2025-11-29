import pytest
from src.services.client_profile.service import ClientProfileService
from src.domain.models.client_profile import ClientIdentifier

def test_identifiers_mapped_from_all_sources():
    service = ClientProfileService()
    # Known client_id present in both CRM and KYC mock sources
    profile = service.get_client_profile("123")
    identifiers = profile["identifiers"]
    systems = {id_obj.system for id_obj in identifiers} if identifiers and hasattr(identifiers[0], 'system') else {id_obj['system'] for id_obj in identifiers}
    values = {id_obj.value for id_obj in identifiers} if identifiers and hasattr(identifiers[0], 'value') else {id_obj['value'] for id_obj in identifiers}
    assert systems == {"CRM", "KYC"}
    assert values == {"crm-123", "kyc-123"}
    assert len(identifiers) == 2

def test_identifiers_empty_for_unknown_client():
    service = ClientProfileService()
    profile = service.get_client_profile("notfound")
    assert profile["identifiers"] == []

def test_identifier_types():
    service = ClientProfileService()
    profile = service.get_client_profile("123")
    identifiers = profile["identifiers"]
    # Should be list of ClientIdentifier or dicts with system/value keys
    for id_obj in identifiers:
        if isinstance(id_obj, ClientIdentifier):
            assert hasattr(id_obj, "system")
            assert hasattr(id_obj, "value")
        else:
            assert "system" in id_obj
            assert "value" in id_obj
