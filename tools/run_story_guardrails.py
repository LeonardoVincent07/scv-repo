#!/usr/bin/env python
"""
Run guardrail checks for one or more Stories.

MVP:
- Deterministic checks only (no external calls, no network).
- Write guardrail evidence to evidence/guardrails/<STORY_ID>.json
- Update guardrail_adherence: pass|fail in the Story markdown front matter.
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Repo root + sys.path
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Story configuration (guardrails are registered explicitly)
# ---------------------------------------------------------------------------

STORY_CONFIG: Dict[str, Dict[str, Any]] = {}


def _register_story(
    story_id: str,
    story_file: Path,
    check_func: Callable[[], Tuple[bool, str]],
    guardrails_checked: List[str],
) -> None:
    STORY_CONFIG[story_id] = {
        "story_file": story_file,
        "check_func": check_func,
        "guardrails_checked": guardrails_checked,
    }


# ---------------------------------------------------------------------------
# Guardrail checks (deterministic)
# ---------------------------------------------------------------------------


def check_backend_health_endpoint() -> Tuple[bool, str]:
    """
    Guardrail for ST-00: backend health endpoint exists and returns expected payload.
    """
    try:
        from fastapi.testclient import TestClient
        from app_backend.main import app
    except Exception as exc:
        return False, f"Import error in /health guardrail check: {exc!r}"

    try:
        client = TestClient(app)
        response = client.get("/health")
    except Exception as exc:
        return False, f"Error calling /health in guardrail check: {exc!r}"

    if response.status_code != 200:
        return False, f"/health returned HTTP {response.status_code}, expected 200."

    try:
        data = response.json()
    except Exception as exc:
        return False, f"/health did not return valid JSON: {exc!r}"

    if not isinstance(data, dict):
        return False, f"/health JSON payload must be an object; got {type(data).__name__}."

    if data.get("status") != "ok":
        return False, f"/health JSON must include status='ok'; got {data!r}"

    return True, "/health returns 200 with JSON {'status': 'ok'}."


def check_client_profile_data_model_adherence() -> Tuple[bool, str]:
    try:
        from src.services.client_profile.service import ClientProfileService
        from src.domain.models.client_profile import ClientProfile
    except Exception as exc:
        return False, f"Import error in profile data-model guardrail check: {exc!r}"

    try:
        service = ClientProfileService()
        profile = service.get_client_profile("123")
    except Exception as exc:
        return False, f"Error calling get_client_profile in guardrail check: {exc!r}"

    if not isinstance(profile, dict):
        return False, f"get_client_profile must return dict; got {type(profile).__name__}."

    field_names = {f.name for f in dataclasses.fields(ClientProfile)}
    missing = sorted([name for name in field_names if name not in profile])
    if missing:
        return False, f"Profile missing required field(s): {missing!r}"

    return True, "ClientProfileService.get_client_profile returns a dict matching ClientProfile fields."


def check_st_09_match_by_tax_id() -> Tuple[bool, str]:
    try:
        from src.services.client_profile.service import ClientProfileService
    except Exception as exc:
        return False, f"Import error in ST-09 guardrail check: {exc!r}"

    service = ClientProfileService()
    service.sources = [service._mock_crm_source, service._mock_kyc_source]

    profile = service.get_client_profile("123")
    profiles = [profile]

    matches = service.match_by_tax_id(profiles, "TAX-001")

    if not isinstance(matches, list):
        return False, "ST-09: match_by_tax_id must return a list."

    if len(matches) != 1:
        return False, f"ST-09: expected exactly one match, got {len(matches)}."

    match = matches[0]
    raw_sources = match.get("raw_sources", {})
    crm_source = raw_sources.get("CRM", {})

    if crm_source.get("tax_id") != "TAX-001":
        return False, "ST-09: matched profile does not contain the requested tax_id in raw_sources."

    return True, "ST-09: match_by_tax_id returns only profiles with the requested tax_id."


# ---------------------------------------------------------------------------
# Register stories
# ---------------------------------------------------------------------------

_register_story(
    "ST-00",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-00-backend-api-availability.md",
    check_backend_health_endpoint,
    [
        "Import FastAPI app from app_backend.main",
        "GET /health via TestClient",
        "Assert HTTP 200",
        "Assert JSON body contains {'status': 'ok'}",
    ],
)

_register_story(
    "ST-03",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-03_map_identity_fields.md",
    check_client_profile_data_model_adherence,
    [
        "Import ClientProfileService and ClientProfile dataclass",
        "Call ClientProfileService.get_client_profile('123')",
        "Assert returned object is dict",
        "Assert dict contains all ClientProfile dataclass field keys",
    ],
)

_register_story(
    "ST-04",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-04_map_identifiers.md",
    check_client_profile_data_model_adherence,
    [
        "Import ClientProfileService and ClientProfile dataclass",
        "Call ClientProfileService.get_client_profile('123')",
        "Assert returned object is dict",
        "Assert dict contains all ClientProfile dataclass field keys",
    ],
)

_register_story(
    "ST-09",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-09_match_by_tax_id.md",
    check_st_09_match_by_tax_id,
    [
        "Import ClientProfileService",
        "Set deterministic mock sources (CRM, KYC)",
        "Call match_by_tax_id(profiles, 'TAX-001')",
        "Assert list return type",
        "Assert exactly one match",
        "Assert matched profile raw_sources.CRM.tax_id == 'TAX-001'",
    ],
)

_register_story(
    "ST-20",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-20_assemble_base_profile.md",
    check_client_profile_data_model_adherence,
    [
        "Import ClientProfileService and ClientProfile dataclass",
        "Call ClientProfileService.get_client_profile('123')",
        "Assert returned object is dict",
        "Assert dict contains all ClientProfile dataclass field keys",
    ],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_guardrail_evidence(
    story_id: str,
    passed: bool,
    message: str,
    guardrails_checked: List[str],
    warnings_captured: List[Dict[str, Any]],
    warnings_count: int,
) -> Path:
    results_dir = REPO_ROOT / "evidence" / "guardrails"
    results_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = results_dir / f"{story_id}.json"
    payload = {
        "story_id": story_id,
        "passed": passed,
        "message": message,
        "guardrails_checked": guardrails_checked,
        "warnings_count": warnings_count,
        "warnings": warnings_captured,
    }
    evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f">>> Wrote guardrail evidence for {story_id} to "
        f"{evidence_path.relative_to(REPO_ROOT)}"
    )
    return evidence_path


def update_story_guardrail_adherence(story_file: Path, passed: bool) -> None:
    status = "pass" if passed else "fail"

    text = story_file.read_text(encoding="utf-8")
    pattern = r"(^guardrail_adherence:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(
            f"Story file {story_file} does not contain a guardrail_adherence line."
        )

    story_file.write_text(new_text, encoding="utf-8")
    print(f">>> Updated {story_file.relative_to(REPO_ROOT)} -> guardrail_adherence: {status}")


def run_guardrail_for_story(story_id: str) -> Tuple[bool, str]:
    config = STORY_CONFIG[story_id]
    story_file: Path = config["story_file"]  # type: ignore[assignment]
    check_func: Callable[[], Tuple[bool, str]] = config["check_func"]  # type: ignore[assignment]
    guardrails_checked: List[str] = config["guardrails_checked"]  # type: ignore[assignment]

    warnings_captured: List[Dict[str, Any]] = []
    warnings_count = 0

    passed, message = check_func()

    write_guardrail_evidence(
        story_id=story_id,
        passed=passed,
        message=message,
        guardrails_checked=guardrails_checked,
        warnings_captured=warnings_captured,
        warnings_count=warnings_count,
    )

    update_story_guardrail_adherence(story_file, passed)
    return passed, message


def main(argv: List[str]) -> int:
    """
    Usage:
      python tools/run_story_guardrails.py          # run for all configured Stories
      python tools/run_story_guardrails.py ST-03    # run for a single Story
    """
    if len(argv) > 1:
        story_id = argv[1].upper()
        if story_id not in STORY_CONFIG:
            print(f"ERROR: Story {story_id!r} is not configured in STORY_CONFIG.")
            print(f"Known stories: {', '.join(sorted(STORY_CONFIG.keys()))}")
            return 1
        requested_ids = [story_id]
    else:
        requested_ids = sorted(STORY_CONFIG.keys())

    overall_exit = 0
    for sid in requested_ids:
        print(f"\n=== Guardrails for Story {sid} ===")
        passed, _ = run_guardrail_for_story(sid)
        if not passed:
            overall_exit = 1

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))



