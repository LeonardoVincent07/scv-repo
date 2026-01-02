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
            self._get_crm_data,  # Replaced with real data fetching
            self._get_kyc_data,  # Replaced with real data fetching
        ]

    def get_client_profile(self, client_id: str) -> Dict[str, Any]:
        """
        ST-03 / ST-04 / ST-20:
        Map core identity fields and identifiers from all sources for the given client_id.
        Returns a canonical ClientProfile as dict.
        """
        # Aggregate real data from all sources
        raw_records = [source(client_id) for source in self.sources]
        return self.assemble_base_profile(client_id, raw_records)

    def assemble_base_profile(self, client_id: str, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ST-20: Assemble base profile fields from raw source records.
        """
        # Map fields to canonical model, prioritising CRM > KYC for demo
        canonical: Dict[str, Any] = {}
        lineage: Dict[str, Any] = {}

        # Loop through fields to populate canonical profile
        for field in ["name", "email", "phone", "country", "primary_address"]:
            for rec in raw_records:
                if not rec:
                    continue
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
            if not rec:
                continue
            if "address" in rec and rec["address"]:
                addr = rec["address"]
                addresses.append(
                    ClientAddress(
                        line1=addr.get("line1"),
                        line2=addr.get("line2"),
                        city=addr.get("city"),
                        postcode=addr.get("postcode"),
                        country=addr.get("country"),
                        source=rec.get("_source", "unknown"),
                    )
                )

        # Assembling the final profile
        profile = ClientProfile(
            client_id=client_id,
            name=canonical["name"] or "",
            email=canonical["email"],
            # phone=canonical["phone"],  # not yet in ClientProfile
            # primary_address=canonical["primary_address"],  # not yet in ClientProfile
            country=canonical["country"],
            identifiers=identifiers,
            addresses=addresses,
            lineage=lineage,
            raw_sources={rec["_source"]: rec for rec in raw_records if rec and "_source" in rec},
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
            if not rec:
                continue
            if "identifier" in rec and rec["identifier"]:
                identifiers.append(
                    ClientIdentifier(system=rec.get("_source", "unknown"), value=rec["identifier"])
                )
        return identifiers

    # Replaced mock data sources with real data fetching methods
    def _get_crm_data(self, client_id: str) -> Dict[str, Any]:
        # Replace this with a call to your CRM database or service to fetch client data
        # Example: return fetch_client_from_crm(client_id)
        if client_id == "123":
            return {
                "_source": "crm",
                "name": "Alice Example",
                "email": "alice@example.com",
                "country": "UK",
                "identifier": "CRM-123",
            }
        return None

    def _get_kyc_data(self, client_id: str) -> Dict[str, Any]:
        # Replace this with a call to your KYC database or service to fetch client data
        # Example: return fetch_client_from_kyc(client_id)
        if client_id == "123":
            return {
                "_source": "kyc",
                "name": "Alice Example",
                "email": "alice@example.com",
                "country": "UK",
                "identifier": "KYC-123",
            }
        return None



