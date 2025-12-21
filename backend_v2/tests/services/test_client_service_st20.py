import pytest
from unittest.mock import MagicMock

from app.services.client_service import ClientService


class DummyClient:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_get_returns_full_ldm_profile_shape(monkeypatch):
    db = MagicMock()
    dummy = DummyClient(
        id=1,
        full_name="Jane Doe",
        email="jane@example.com",
        country="UK",
    )

    from app.repositories.client_repository import ClientRepository
    monkeypatch.setattr(ClientRepository, "get", MagicMock(return_value=dummy))

    profile = ClientService.get(db, 1)

    assert profile == {
        "client_id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "country": "UK",
        "identifiers": [],
        "addresses": [],
        "lineage": {},
        "quality": {},
        "metadata": {},
        "raw_sources": [],
    }


def test_get_is_deterministic_for_same_input(monkeypatch):
    db = MagicMock()
    dummy = DummyClient(
        id=1,
        full_name="Jane Doe",
        email="jane@example.com",
        country="UK",
    )

    from app.repositories.client_repository import ClientRepository
    monkeypatch.setattr(ClientRepository, "get", MagicMock(return_value=dummy))

    profile_a = ClientService.get(db, 1)
    profile_b = ClientService.get(db, 1)

    assert profile_a == profile_b


def test_get_returns_none_when_client_missing(monkeypatch):
    db = MagicMock()

    from app.repositories.client_repository import ClientRepository
    monkeypatch.setattr(ClientRepository, "get", MagicMock(return_value=None))

    profile = ClientService.get(db, 999)

    assert profile is None

