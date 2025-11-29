from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ClientIdentifier:
    """
    Represents an identifier for a client from a specific upstream system.
    """
    system: str        # e.g. "CRM", "KYC"
    value: str         # e.g. "12345"


@dataclass
class ClientAddress:
    """
    Represents a normalised address for a client.
    Optional in MVP, but needed for merge, lineage, and quality features.
    """
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None   # Upstream system this address came from


@dataclass
class ClientProfile:
    """
    Canonical Single Client View logical data model.
    This is the semantic target for all ingestion, normalisation, match/merge,
    lineage propagation, quality scoring, and profile assembly stories.
    """
    client_id: str
    name: str

    email: Optional[str] = None
    country: Optional[str] = None

    identifiers: List[ClientIdentifier] = field(default_factory=list)
    addresses: List[ClientAddress] = field(default_factory=list)

    # Where each field came from, and under what conditions
    lineage: Dict[str, Any] = field(default_factory=dict)

    # Data quality indicators (freshness, completeness, confidence)
    quality: Dict[str, float] = field(default_factory=dict)

    # Additional metadata (timestamps, merge strategy flags, raw source info)
    metadata: Dict[str, str] = field(default_factory=dict)

    # Optional raw inputs (keyed by upstream system)
    raw_sources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
