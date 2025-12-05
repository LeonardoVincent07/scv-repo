#!/usr/bin/env python
"""
Seed additional demo clients into the SCV database via the /ingest endpoint.

NOTE:
- This script ONLY creates NEW clients:
    - C-004, C-005, C-006, C-007
- It does NOT touch C-001, C-002, C-003 that you have already created.

Clients:

- C-004: Delta Manufacturing
    - CRM + KYC + VENDOR (external) sources
    - Slight differences in names, emails, addresses

- C-005: Eastbridge Holdings
    - Single CRM record with slightly messy data

- C-006: Flextronics / Flextronix
    - CRM + KYC with shared tax_id="TAX-777"
    - Great example for ST-09 match-by-tax-id

- C-007: GreyLake Partners
    - CRM + KYC + VENDOR sources
    - Conflicting emails, address formats, country codes

Run (from repo root, with backend running on 127.0.0.1:8000):

    python tools/seed_demo_data.py
"""

import requests

BACKEND_BASE_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{BACKEND_BASE_URL}/ingest"


def ingest_record(rec: dict):
    """Send a single record to the backend /ingest endpoint."""
    wire_payload = {
        "client_id": rec["client_id"],
        "system": rec["system"],
        "payload": rec["payload"],  # dict, not JSON string
    }

    print(f"---> Ingesting {rec['system']} record for client {rec['client_id']}")

    resp = requests.post(INGEST_URL, json=wire_payload)

    if not resp.ok:
        print(f"!! Failed ({resp.status_code}): {resp.text}")
        resp.raise_for_status()

    data = resp.json()
    print(f"     OK: id={data.get('id')} system={data.get('system')}")
    return data


def main():
    print("=== Seeding EXTRA SCV demo data via /ingest ===")
    print(f"Target backend: {BACKEND_BASE_URL}\n")

    demo_records = [
        # ------------------------------------------------------------------
        # C-004 — Delta Manufacturing (rich multi-source example)
        # ------------------------------------------------------------------
        {
            "client_id": "C-004",
            "system": "CRM",
            "payload": {
                "_source": "CRM",
                "client_id": "C-004",
                "name": "Delta Manufacturing Ltd",
                "email": "info@delta-mfg.com",
                "phone": "+44 20 8000 4004",
                "country": "GB",
                "tax_id": "TAX-004",
                "registration_number": "REG-DELTA-01",
                "address_line1": "10 Industry Way",
                "address_city": "Birmingham",
                "postcode": "B1 2AA",
            },
        },
        {
            "client_id": "C-004",
            "system": "KYC",
            "payload": {
                "_source": "KYC",
                "client_id": "C-004",
                "name": "Delta MFG Limited",
                "email": "kyc@delta-mfg.com",
                "country": "UK",
                "tax_id": "TAX-004",
                "kyc_risk_rating": "LOW",
                "address_line1": "10 Industry Way",
                "address_city": "Birmingham",
                "postcode": "B1 2AA",
            },
        },
        {
            "client_id": "C-004",
            "system": "VENDOR",
            "payload": {
                "_source": "VENDOR",
                "client_id": "C-004",
                "name": "Delta Manufacturing Limited",
                "email": "compliance@delta-mfg.com",
                "country": "GBR",
                "tax_id": "TAX-004",
                "external_reference": "VEN-DELTA-2025",
            },
        },

        # ------------------------------------------------------------------
        # C-005 — Eastbridge Holdings (messy CRM-only)
        # ------------------------------------------------------------------
        {
            "client_id": "C-005",
            "system": "CRM",
            "payload": {
                "_source": "CRM",
                "client_id": "C-005",
                "name": "EASTBRIDGE HOLDINGS PLC",  # upper case
                "email": "contact@eastbridge-holdings.com",
                "phone": "+44 20 7005 5005",
                "country": "GB",
                "tax_id": None,  # intentionally missing tax id
                "registration_number": "REG-EAST-01",
                "identifier_1": "CRM-EAST-001",
                "identifier_2": "ALT-EAST-XYZ",
            },
        },

        # ------------------------------------------------------------------
        # C-006 — Flextronics / Flextronix (tax-id merge demo)
        # ------------------------------------------------------------------
        {
            "client_id": "C-006",
            "system": "CRM",
            "payload": {
                "_source": "CRM",
                "client_id": "C-006",
                "name": "Flextronics PLC",
                "email": "info@flextronics.com",
                "phone": "+44 20 7010 6006",
                "country": "GB",
                "tax_id": "TAX-777",
                "registration_number": "REG-FLEX-01",
            },
        },
        {
            "client_id": "C-006",
            "system": "KYC",
            "payload": {
                "_source": "KYC",
                "client_id": "C-006",
                "name": "Flextronix Plc",  # slight name variation
                "email": "kyc@flextronix.com",
                "country": "UK",
                "tax_id": "TAX-777",  # shared tax id → ST-09 demo
                "kyc_risk_rating": "MEDIUM",
            },
        },

        # ------------------------------------------------------------------
        # C-007 — GreyLake Partners (three conflicting sources)
        # ------------------------------------------------------------------
        {
            "client_id": "C-007",
            "system": "CRM",
            "payload": {
                "_source": "CRM",
                "client_id": "C-007",
                "name": "Greylake Partners LLP",
                "email": "info@greylakepartners.co.uk",
                "phone": "+44 20 7020 7007",
                "country": "GB",
                "tax_id": "TAX-007",
                "registration_number": "REG-GREY-01",
                "address_line1": "50 Riverside Walk",
                "address_city": "London",
                "postcode": "EC2R 8AH",
            },
        },
        {
            "client_id": "C-007",
            "system": "KYC",
            "payload": {
                "_source": "KYC",
                "client_id": "C-007",
                "name": "GreyLake Partners LLP",  # different capitalisation
                "email": "kyc@greylakepartners.com",
                "country": "UK",
                "tax_id": "TAX-007",
                "kyc_risk_rating": "HIGH",
                "address_line1": "50 Riverside Walk",
                "address_city": "London",
                "postcode": "EC2R 8AH",
            },
        },
        {
            "client_id": "C-007",
            "system": "VENDOR",
            "payload": {
                "_source": "VENDOR",
                "client_id": "C-007",
                "name": "Greylake Partners LLP",
                "email": "operations@greylakepartners.com",
                "country": "GBR",
                "tax_id": "TAX-007",
                "external_reference": "VEN-GREY-2025",
            },
        },
    ]

    for rec in demo_records:
        ingest_record(rec)

    print("\n=== Extra demo data seeded successfully ===")
    print("You now have additional clients:")
    print("  • C-004  (Delta Manufacturing – rich multi-source)")
    print("  • C-005  (Eastbridge Holdings – messy CRM-only)")
    print("  • C-006  (Flextronics/Flextronix – tax-id match demo)")
    print("  • C-007  (GreyLake Partners – conflicting multi-source)")
    print()


if __name__ == "__main__":
    main()


