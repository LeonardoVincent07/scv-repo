from sqlalchemy.orm import Session

from app.schemas.client import ClientCreate
from app.schemas.account import AccountCreate
from app.schemas.transaction import TransactionCreate
from app.schemas.kyc_flag import KycFlagCreate

from app.services.client_service import ClientService
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.services.kyc_flag_service import KycFlagService

from app.models.client import Client


def seed(db: Session) -> None:
    """
    Seed the database with a small institutional / corporate book.

    Note: this only runs if there are no clients in the database.
    """
    if db.query(Client).count() > 0:
        return

    # ---------- CLIENTS (CORPORATE) ----------

    acme = ClientService.create(
        db,
        ClientCreate(
            external_id="CRM-CORP-001",
            full_name="Acme Manufacturing Ltd",
            email="treasury@acme-mfg.co.uk",
            phone="+44 20 7000 1001",
            primary_address="10 Foundry Park, Birmingham, B1 2AB, United Kingdom",
            country="UK",
            tax_id="GB999000111",
            segment="Corporate – Mid Cap",
            risk_rating="MEDIUM",
        ),
    )

    northbridge = ClientService.create(
        db,
        ClientCreate(
            external_id="CRM-FI-002",
            full_name="Northbridge Capital Markets LLP",
            email="ops@northbridgecm.com",
            phone="+44 20 7100 2200",
            primary_address="25 Bishopsgate, London EC2N 4AA, United Kingdom",
            country="UK",
            tax_id="GB777123456",
            segment="Financial Institution – Broker/Dealer",
            risk_rating="HIGH",
        ),
    )

    eurotech = ClientService.create(
        db,
        ClientCreate(
            external_id="CRM-CORP-003",
            full_name="EuroTech Components AG",
            email="finance@eurotech-ag.de",
            phone="+49 69 9000 3300",
            primary_address="Friedrich-Ebert-Anlage 12, 60325 Frankfurt, Germany",
            country="DE",
            tax_id="DE311445566",
            segment="Corporate – Large Cap",
            risk_rating="LOW",
        ),
    )

    greenfields = ClientService.create(
        db,
        ClientCreate(
            external_id="CRM-FUND-004",
            full_name="Greenfields Global Opportunities Fund",
            email="fundops@greenfieldsfund.com",
            phone="+44 20 7200 4455",
            primary_address="8 St James’s Square, London SW1Y 4JU, United Kingdom",
            country="UK",
            tax_id="JE55001122",
            segment="Asset Manager – Fund",
            risk_rating="HIGH",
        ),
    )

    cityhealth = ClientService.create(
        db,
        ClientCreate(
            external_id="CRM-CORP-005",
            full_name="CityHealth NHS Services Consortium",
            email="finance@cityhealth-consortium.org.uk",
            phone="+44 161 400 8800",
            primary_address="120 Deansgate, Manchester M3 2GH, United Kingdom",
            country="UK",
            tax_id="GB660009999",
            segment="Public Sector / Healthcare",
            risk_rating="MEDIUM",
        ),
    )

    # ---------- ACCOUNTS ----------

    # Acme – operating GBP account, USD account
    acme_gbp = AccountService.create(
        db,
        AccountCreate(
            client_id=acme.id,
            account_number="ACME-GBP-001",
            account_type="OPERATING",
            currency="GBP",
            status="OPEN",
        ),
    )
    acme_usd = AccountService.create(
        db,
        AccountCreate(
            client_id=acme.id,
            account_number="ACME-USD-001",
            account_type="OPERATING",
            currency="USD",
            status="OPEN",
        ),
    )

    # Northbridge – client money & margin
    nb_client = AccountService.create(
        db,
        AccountCreate(
            client_id=northbridge.id,
            account_number="NB-CM-001",
            account_type="CLIENT_MONEY",
            currency="GBP",
            status="OPEN",
        ),
    )
    nb_margin = AccountService.create(
        db,
        AccountCreate(
            client_id=northbridge.id,
            account_number="NB-MRG-001",
            account_type="MARGIN",
            currency="USD",
            status="OPEN",
        ),
    )

    # EuroTech – EUR operating
    euro_eur = AccountService.create(
        db,
        AccountCreate(
            client_id=eurotech.id,
            account_number="ET-EUR-001",
            account_type="OPERATING",
            currency="EUR",
            status="OPEN",
        ),
    )

    # Greenfields – subscription & redemption cash
    gf_sub = AccountService.create(
        db,
        AccountCreate(
            client_id=greenfields.id,
            account_number="GF-SUB-001",
            account_type="SUBSCRIPTIONS",
            currency="USD",
            status="OPEN",
        ),
    )
    gf_red = AccountService.create(
        db,
        AccountCreate(
            client_id=greenfields.id,
            account_number="GF-RED-001",
            account_type="REDEMPTIONS",
            currency="USD",
            status="OPEN",
        ),
    )

    # CityHealth – GBP payments account
    ch_gbp = AccountService.create(
        db,
        AccountCreate(
            client_id=cityhealth.id,
            account_number="CH-GBP-001",
            account_type="OPERATING",
            currency="GBP",
            status="OPEN",
        ),
    )

    # ---------- TRANSACTIONS (HIGH-LEVEL) ----------

    # Acme GBP
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=acme_gbp.id,
            trade_date="2025-01-05",
            value_date="2025-01-05",
            amount=1_250_000.00,
            currency="GBP",
            txn_type="CREDIT",
            description="Quarterly invoice receipts – UK distributors",
        ),
    )
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=acme_gbp.id,
            trade_date="2025-01-08",
            value_date="2025-01-08",
            amount=-420_000.00,
            currency="GBP",
            txn_type="DEBIT",
            description="Payroll and supplier payments",
        ),
    )

    # Acme USD
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=acme_usd.id,
            trade_date="2025-01-10",
            value_date="2025-01-11",
            amount=900_000.00,
            currency="USD",
            txn_type="CREDIT",
            description="Export receipts – US customer",
        ),
    )

    # Northbridge client money
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=nb_client.id,
            trade_date="2025-02-01",
            value_date="2025-02-01",
            amount=35_000_000.00,
            currency="GBP",
            txn_type="CREDIT",
            description="Client collateral top-up",
        ),
    )
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=nb_client.id,
            trade_date="2025-02-02",
            value_date="2025-02-02",
            amount=-12_500_000.00,
            currency="GBP",
            txn_type="DEBIT",
            description="Daily variation margin outflow",
        ),
    )

    # Northbridge margin USD
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=nb_margin.id,
            trade_date="2025-02-03",
            value_date="2025-02-04",
            amount=7_500_000.00,
            currency="USD",
            txn_type="CREDIT",
            description="Initial margin received on cleared swaps",
        ),
    )

    # EuroTech EUR
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=euro_eur.id,
            trade_date="2025-01-15",
            value_date="2025-01-15",
            amount=4_200_000.00,
            currency="EUR",
            txn_type="CREDIT",
            description="Receivables from OEM contracts",
        ),
    )
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=euro_eur.id,
            trade_date="2025-01-18",
            value_date="2025-01-19",
            amount=-3_100_000.00,
            currency="EUR",
            txn_type="DEBIT",
            description="Raw materials purchase – multi-country suppliers",
        ),
    )

    # Greenfields subscriptions / redemptions
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=gf_sub.id,
            trade_date="2025-03-01",
            value_date="2025-03-02",
            amount=65_000_000.00,
            currency="USD",
            txn_type="CREDIT",
            description="Monthly investor subscriptions",
        ),
    )
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=gf_red.id,
            trade_date="2025-03-05",
            value_date="2025-03-06",
            amount=-18_500_000.00,
            currency="USD",
            txn_type="DEBIT",
            description="Quarterly investor redemptions",
        ),
    )

    # CityHealth GBP
    TransactionService.create(
        db,
        TransactionCreate(
            account_id=ch_gbp.id,
            trade_date="2025-01-07",
            value_date="2025-01-07",
            amount=9_750_000.00,
            currency="GBP",
            txn_type="CREDIT",
            description="NHS commissioning inflow – London region",
        ),
    )

    # ---------- KYC FLAGS ----------

    KycFlagService.create(
        db,
        KycFlagCreate(
            client_id=northbridge.id,
            code="HIGH_TRADING_VOLUME",
            description="Daily derivatives margin flows above defined threshold",
            status="OPEN",
            created_at="2024-12-15",
        ),
    )

    KycFlagService.create(
        db,
        KycFlagCreate(
            client_id=greenfields.id,
            code="UBO_COMPLEX_STRUCTURE",
            description="Layered fund / SPV structure – enhanced due diligence required",
            status="OPEN",
            created_at="2024-11-01",
        ),
    )

    KycFlagService.create(
        db,
        KycFlagCreate(
            client_id=acme.id,
            code="SANCTIONS_SCREENING_HIT",
            description="False positive – name match to restricted entity, monitored",
            status="CLOSED",
            created_at="2023-06-10",
            resolved_at="2023-06-12",
        ),
    )
