import pytest
from src.api.http.client_profile_api import ClientProfileAPI


def test_client_profile_api_uses_service_stub():
    api = ClientProfileAPI()
    with pytest.raises(NotImplementedError):
        api.get_client_profile("dummy-id")
