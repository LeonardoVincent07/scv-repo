import pytest
from src.services.client_profile.service import ClientProfileService


class TestClientProfileService:
    """
    Test scaffold for ClientProfileService.

    NOTE:
    - Structure and naming follow the MissionSmith scaffold.
    - Real test cases will be generated from story definitions.
    """

    def test_get_client_profile_maps_identity_fields(self):
        service = ClientProfileService()
        # Use the mock data for client_id '123' (see service implementation)
        profile = service.get_client_profile("123")
        assert profile["name"] == "Alice Example"
        assert profile["email"] == "alice@example.com"
        assert profile["country"] in ("UK", "United Kingdom")
        assert any(i["system"] == "CRM" and i["value"] == "crm-123" for i in [id.__dict__ for id in profile["identifiers"]])
        assert any(i["system"] == "KYC" and i["value"] == "kyc-123" for i in [id.__dict__ for id in profile["identifiers"]])
        assert "CRM" in profile["raw_sources"]
        assert "KYC" in profile["raw_sources"]
