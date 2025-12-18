# backend_v2/app/schemas/scv_profile.py
"""
SCV Profile Contract (Baseline)

This file defines the *baseline* response contract for:
  GET /clients/{client_id}/profile

Principles:
- This is a contract boundary for the frontend.
- Top-level legacy fields MUST remain present (even if null).
- Canonical SCV keys MUST exist even when empty.

Note:
- We intentionally keep `client` and `accounts` as loosely-typed objects for now
  because the endpoint currently uses `jsonable_encoder(...)` on SQLAlchemy models.
  We can tighten types later without changing the UI contract.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    model_config = ConfigDict(extra="allow")

    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None


class OperationalState(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    as_of: Optional[str] = None
    processing_stage: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class TradeHistoryRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    trade_id: Optional[int] = None
    account_id: Optional[int] = None
    trade_date: Optional[str] = None
    value_date: Optional[str] = None
    asset_class: Optional[str] = None
    instrument: Optional[str] = None
    direction: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    pnl: Optional[float] = None

    # Raw/source fields (kept for expandable JSON / debugging)
    amount: Optional[float] = None
    currency: Optional[str] = None
    txn_type: Optional[str] = None
    description: Optional[str] = None


class SCVClientProfileResponse(BaseModel):
    """
    Baseline contract for the SCV profile endpoint.

    Contains:
    - Legacy/top-level fields used by the existing UI header
    - Canonical SCV keys required by SCV_CANONICAL_STATE.md
    """
    model_config = ConfigDict(extra="allow")

    # ---- legacy/top-level (do not remove) ----
    client_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    segment: Optional[str] = None
    risk_rating: Optional[str] = None
    addresses: List[Address] = Field(default_factory=list)
    operational_state: OperationalState = Field(default_factory=OperationalState)

    # ---- canonical SCV keys (must exist even if empty) ----
    client: Dict[str, Any] = Field(default_factory=dict)
    accounts: List[Dict[str, Any]] = Field(default_factory=list)
    match_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    trade_history: List[TradeHistoryRow] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    regulatory_enrichment: Dict[str, Any] = Field(default_factory=dict)
    evidence_artefacts: List[Dict[str, Any]] = Field(default_factory=list)
