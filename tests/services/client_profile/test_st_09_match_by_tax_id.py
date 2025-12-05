from src.services.client_profile.service import ClientProfileService


def test_match_by_tax_id_exact():
    service = ClientProfileService()

    # Patch CRM source to include a tax_id for this client
    service._mock_crm_source = lambda client_id: {
        "_source": "CRM",
        "identifier": "crm-123",
        "name": "Alice Example",
        "email": "alice@example.com",
        "country": "UK",
        "tax_id": "TAX-001",
    } if client_id == "123" else {"_source": "CRM"}

    # Rebuild sources list so it uses the patched function
    service.sources = [service._mock_crm_source, service._mock_kyc_source]

    profile = service.get_client_profile("123")

    # Sanity check the raw source has the expected tax_id
    assert profile["raw_sources"]["CRM"]["tax_id"] == "TAX-001"

    # ACT: call the real service method
    matches = service.match_by_tax_id([profile], "TAX-001")

    # ASSERT: one match, and it's the correct client
    assert len(matches) == 1
    assert matches[0]["client_id"] == "123"


def test_match_by_tax_id_no_match():
    service = ClientProfileService()

    service._mock_crm_source = lambda client_id: {
        "_source": "CRM",
        "identifier": "crm-999",
        "name": "Bob Example",
        "email": "bob@example.com",
        "country": "UK",
        "tax_id": "TAX-999",
    } if client_id == "999" else {"_source": "CRM"}

    service.sources = [service._mock_crm_source, service._mock_kyc_source]

    profile = service.get_client_profile("999")

    matches = service.match_by_tax_id([profile], "TAX-001")
    assert len(matches) == 0

