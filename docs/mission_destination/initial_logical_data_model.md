# Initial Logical Data Model (LDM)
**MissionDestination**
**Single Client View (SCV)**

## 1. Purpose
This document defines the **Initial Logical Data Model** for the Single Client View (SCV) application.
It establishes the **canonical semantic representation of a client**, which all ingestion,
normalisation, matching, merging, lineage, quality, and API features will converge toward.

The Initial Logical Data Model is:
- technology-agnostic
- storage-agnostic
- canonical across all source systems
- stable across all Stories
- the semantic target for the behaviours defined in Epics, Features, and Stories

It is **not** a physical database schema.  
It is the logical definition of what a “client” means inside the SCV domain.

## 2. Canonical Entities

### 2.1 ClientProfile
Represents the unified, deduplicated profile of a client.

| Field | Type | Description |
|-------|------|-------------|
| client_id | str | Internal SCV identifier |
| name | str | Canonical client name |
| email | Optional[str] | Canonical email |
| country | Optional[str] | Country associated with the client |
| identifiers | List[ClientIdentifier] | Identifiers from upstream systems |
| addresses | List[ClientAddress] | Normalised address objects |
| lineage | Dict[str, Any] | Provenance metadata |
| quality | Dict[str, float] | Freshness, completeness, confidence |
| metadata | Dict[str, str] | Timestamps, merge strategies, flags |
| raw_sources | Dict[str, Dict[str, Any]] | Raw source payloads |

### 2.2 ClientIdentifier
| Field | Type | Description |
|-------|------|-------------|
| system | str | Upstream system name |
| value | str | Identifier in that system |

### 2.3 ClientAddress
| Field | Type | Description |
|-------|------|-------------|
| line1 | Optional[str] | Address line 1 |
| line2 | Optional[str] | Address line 2 |
| city | Optional[str] | City |
| postcode | Optional[str] | Postal code |
| country | Optional[str] | ISO country |
| source | Optional[str] | System contributing the address |

## 3. Python Representation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ClientIdentifier:
    system: str
    value: str

@dataclass
class ClientAddress:
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None

@dataclass
class ClientProfile:
    client_id: str
    name: str

    email: Optional[str] = None
    country: Optional[str] = None

    identifiers: List[ClientIdentifier] = field(default_factory=list)
    addresses: List[ClientAddress] = field(default_factory=list)

    lineage: Dict[str, Any] = field(default_factory=dict)
    quality: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    raw_sources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
```

## 4. Next Steps
- Add this model to `src/domain/models/client_profile.py`
- Keep structure stable through MVP
- Extend only if new Stories introduce semantic requirements
