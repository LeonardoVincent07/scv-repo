from typing import Dict, Any, List

from src.domain.models.client_profile import ClientProfile, ClientIdentifier, ClientAddress


class ClientProfileService:
    """
    Single Client View – Client Profile Service.

    Implements:
    - ST-03: Map core identity fields from multiple sources to canonical model.
    - ST-04: Map identifiers from all sources.
    - ST-20: Assemble base profile fields from raw source records.
    - ST-09: Match by tax ID across profiles.
    """

    def __init__(self):
        # In a real implementation, these would be injected repositories or data sources
        self.sources = [
            self._mock_crm_source,
            self._mock_kyc_source,
        ]

    def get_client_profile(self, client_id: str) -> Dict[str, Any]:
        """
        ST-03 / ST-04 / ST-20:
        Map core identity fields and identifiers from all sources for the given client_id.
        Returns a canonical ClientProfile as dict.
        """
        # Aggregate raw data from all sources
        raw_records = [source(client_id) for source in self.sources]
        return self.assemble_base_profile(client_id, raw_records)

    def assemble_base_profile(self, client_id: str, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ST-20: Assemble base profile fields from raw source records.
        """
        # Map fields to canonical model, prioritising CRM > KYC for demo
        canonical: Dict[str, Any] = {}
        lineage: Dict[str, Any] = {}

        for field in ["name", "email", "country"]:
            for rec in raw_records:
                if field in rec and rec[field]:
                    canonical[field] = rec[field]
                    lineage[field] = rec.get("_source", "unknown")
                    break
            else:
                canonical[field] = None
                lineage[field] = None

        # Identifiers (ST-04)
        identifiers = self._map_identifiers(raw_records)

        # Addresses (optional, demo only)
        addresses = []
        for rec in raw_records:
            if "address" in rec and rec["address"]:
                addr = rec["address"]
                addresses.append(
                    ClientAddress(
                        line1=addr.get("line1"),
                        line2=addr.get("line2"),
                        city=addr.get("city"),
                        postcode=addr.get("postcode"),
                        country=addr.get("country"),
                        source=rec["_source"],
                    )
                )

        profile = ClientProfile(
            client_id=client_id,
            name=canonical["name"] or "",
            email=canonical["email"],
            country=canonical["country"],
            identifiers=identifiers,
            addresses=addresses,
            lineage=lineage,
            raw_sources={rec["_source"]: rec for rec in raw_records},
        )
        return profile.__dict__

    def match_by_tax_id(self, profiles: List[Dict[str, Any]], tax_id: str) -> List[Dict[str, Any]]:
        """
        ST-09: Exact match by tax ID.

        Returns a list of profiles where any raw source contains the given tax_id.
        """
        matched: List[Dict[str, Any]] = []
        for profile in profiles:
            raw_sources = profile.get("raw_sources", {})
            for source_data in raw_sources.values():
                if source_data.get("tax_id") == tax_id:
                    matched.append(profile)
                    break
        return matched

    def _map_identifiers(self, raw_records: List[Dict[str, Any]]) -> list:
        """
        ST-04: Map identifiers from all sources to canonical ClientIdentifier list.
        """
        identifiers = []
        for rec in raw_records:
            if "identifier" in rec and rec["identifier"]:
                identifiers.append(
                    ClientIdentifier(system=rec["_source"], value=rec["identifier"])
                )
        return identifiers

    def _mock_crm_source(self, client_id: str) -> Dict[str, Any]:
        # Simulate a CRM system record
        if client_id == "123":
            return {
                "_source": "CRM",
                "identifier": "crm-123",
                "name": "Alice Example",
                "email": "alice@example.com",
                "country": "UK",
                "address": {
                    "line1": "1 Main St",
                    "city": "London",
                    "postcode": "E1 1AA",
                    "country": "UK",
                },
            }
        return {"_source": "CRM"}

    def _mock_kyc_source(self, client_id: str) -> Dict[str, Any]:
        # Simulate a KYC system record
        if client_id == "123":
            return {
                "_source": "KYC",
                "identifier": "kyc-123",
                "name": "Alice Example",
                "email": None,
                "country": "United Kingdom",
                "address": {
                    "line1": "1 Main Street",
                    "city": "London",
                    "postcode": "E1 1AA",
                    "country": "United Kingdom",
                },
            }
        return {"_source": "KYC"}
