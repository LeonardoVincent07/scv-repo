import pytest
from src.services.client_search.service import ClientSearchService


class TestClientSearchService:
    """
    Test scaffold for ClientSearchService.
    """

    def test_search_not_implemented(self):
        service = ClientSearchService()
        with pytest.raises(NotImplementedError):
            service.search("dummy query")

