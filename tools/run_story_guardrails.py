#!/usr/bin/env python
"""
Run guardrail checks for one or more Stories and update guardrail_adherence
in each Story's front matter.

For the MVP, the guardrail we enforce is:
- Story output must adhere to the canonical data model.

Specifically for ST-03 / ST-04:
- ClientProfileService.get_client_profile(...) must return a structure
  that matches the ClientProfile dataclass fields and types.
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Callable

# ---------------------------------------------------------------------------
# Repo root + sys.path fix so "src" can be imported
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

# Ensure the repo root is on sys.path so that "src. ..." imports work when this
# script is run as `python tools/run_story_guardrails.py`.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Story configuration
# ---------------------------------------------------------------------------

# Each entry defines:
# - story_file: the markdown Story file
# - check_func: a callable that performs guardrail checks and returns (passed, message)
STORY_CONFIG: Dict[str, Dict[str, Any]] = {}


def _register_story(
    story_id: str,
    story_file: Path,
    check_func: Callable[[], Tuple[bool, str]],
) -> None:
    STORY_CONFIG[story_id] = {
        "story_file": story_file,
        "check_func": check_func,
    }


# ---------------------------------------------------------------------------
# Guardrail checks
# ---------------------------------------------------------------------------

def check_client_profile_data_model_adherence() -> Tuple[bool, str]:
    """
    Guardrail for ClientProfile-producing Stories (ST-03, ST-04).

    Rules:
    - get_client_profile(...) must return a dict
    - Keys of that dict must be a subset of ClientProfile fields
    - Required fields (client_id, name) must be present
    - identifiers must be a List[ClientIdentifier]
    - addresses must be a List[ClientAddress]
    - lineage, quality, metadata, raw_sources must be dicts
    """
    try:
        from src.services.client_profile.service import ClientProfileService
        from src.domain.models.client_profile import (
            ClientProfile,
            ClientIdentifier,
            ClientAddress,
        )
    except Exception as exc:  # pragma: no cover
        return False, f"Import error in guardrail check: {exc!r}"

    service = ClientProfileService()

    # Use the same client_id as the tests; this exercises the normal path
    profile = service.get_client_profile("123")

    if not isinstance(profile, dict):
        return False, "get_client_profile must return a dict derived from ClientProfile."

    # 1) Keys must match the ClientProfile dataclass (no unexpected fields)
    allowed_fields = {f.name for f in dataclasses.fields(ClientProfile)}
    keys = set(profile.keys())
    extra_fields = keys - allowed_fields
    if extra_fields:
        return False, f"Output contains fields not in ClientProfile: {sorted(extra_fields)}"

    required_fields = {"client_id", "name"}
    missing = required_fields - keys
    if missing:
        return False, f"Output is missing required fields: {sorted(missing)}"

    # 2) identifiers must be a list of ClientIdentifier instances
    identifiers = profile.get("identifiers")
    if not isinstance(identifiers, list):
        return False, "identifiers must be a list of ClientIdentifier."
    for idx, item in enumerate(identifiers):
        if not isinstance(item, ClientIdentifier):
            return False, f"identifiers[{idx}] is not a ClientIdentifier instance."

    # 3) addresses must be a list of ClientAddress instances
    addresses = profile.get("addresses")
    if not isinstance(addresses, list):
        return False, "addresses must be a list of ClientAddress."
    for idx, addr in enumerate(addresses):
        if not isinstance(addr, ClientAddress):
            return False, f"addresses[{idx}] is not a ClientAddress instance."

    # 4) lineage, quality, metadata, raw_sources should be dicts
    for field_name in ["lineage", "quality", "metadata", "raw_sources"]:
        value = profile.get(field_name)
        if not isinstance(value, dict):
            return False, f"{field_name} must be a dict; got {type(value).__name__}"

    return True, "Output adheres to ClientProfile data model."


# Register ST-03 and ST-04 (same guardrail, same model)
_register_story(
    "ST-03",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-03_map_identity_fields.md",
    check_client_profile_data_model_adherence,
)

_register_story(
    "ST-04",
    REPO_ROOT
    / "docs"
    / "mission_destination"
    / "stories"
    / "ST-04_map_identifiers.md",
    check_client_profile_data_model_adherence,
)

_register_story(
    "ST-20",
    REPO_ROOT / "docs" / "mission_destination" / "stories" / "ST-20_assemble_base_profile.md",
    check_client_profile_data_model_adherence,
)


# ---------------------------------------------------------------------------
# Helpers: evidence + front-matter update
# ---------------------------------------------------------------------------

def write_guardrail_evidence(
    story_id: str,
    passed: bool,
    message: str,
) -> Path:
    """
    Write a JSON evidence file for guardrail adherence for this Story.
    """
    results_dir = REPO_ROOT / "evidence" / "guardrails"
    results_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = results_dir / f"{story_id}.json"
    payload = {
        "story_id": story_id,
        "passed": passed,
        "message": message,
    }
    evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f">>> Wrote guardrail evidence for {story_id} to {evidence_path.relative_to(REPO_ROOT)}")
    return evidence_path


def update_story_guardrail_adherence(story_file: Path, passed: bool) -> None:
    """
    Replace the first 'guardrail_adherence: ...' line in the Story's front matter.
    """
    if not story_file.exists():
        raise FileNotFoundError(f"Story file not found: {story_file}")

    status = "pass" if passed else "fail"

    text = story_file.read_text(encoding="utf-8")

    pattern = r"(^guardrail_adherence:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(
            f"Story file {story_file} does not contain a guardrail_adherence line to update."
        )

    story_file.write_text(new_text, encoding="utf-8")
    rel = story_file.relative_to(REPO_ROOT)
    print(f">>> Updated {rel} -> guardrail_adherence: {status}")


def run_guardrail_for_story(story_id: str) -> Tuple[bool, str]:
    """
    Run the guardrail check for a single Story:
    - execute the check function
    - write evidence
    - update front matter
    Returns (passed, message).
    """
    config = STORY_CONFIG[story_id]
    story_file: Path = config["story_file"]  # type: ignore[assignment]
    check_func: Callable[[], Tuple[bool, str]] = config["check_func"]  # type: ignore[assignment]

    print(f">>> Running guardrail checks for Story {story_id}")
    passed, message = check_func()

    write_guardrail_evidence(story_id, passed, message)
    update_story_guardrail_adherence(story_file, passed)

    status = "pass" if passed else "fail"
    print(f">>> Story {story_id} guardrail_adherence set to {status}: {message}")
    return passed, message


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

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
