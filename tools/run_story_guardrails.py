#!/usr/bin/env python
"""
Run guardrail checks for one or more Stories.

MVP principles:
- MissionLog is a renderer, not a runner.
- Guardrails are global.
- Applicability is story-scoped (a Story binds to global guardrails via front matter).
- If a guardrail is not applicable, the Story still "passes" guardrails for demo purposes:
  it has not violated any applicable guardrail.

MVP implementation:
- Supports only G03 (LDM adherence) using tools/guardrails/run_g03_ldm.py logic.
- Writes evidence to evidence/guardrails/<STORY_ID>.json
- Updates guardrail_adherence: pass|fail in Story front matter.
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend_v2"

# Ensure backend_v2 is on PYTHONPATH so `import app` works
sys.path.insert(0, str(BACKEND_ROOT))
os.environ["PYTHONPATH"] = str(BACKEND_ROOT)



# ---------------------------------------------------------------------------
# Repo root + sys.path
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


# ---------------------------------------------------------------------------
# Evidence writer
# ---------------------------------------------------------------------------

def write_guardrail_evidence(
    story_id: str,
    passed: bool,
    message: str,
    guardrails_checked: List[str],
    warnings: List[Dict[str, Any]] | None = None,
    warnings_count: int | None = None,
    guardrail_results: List[Dict[str, Any]] | None = None,
) -> Path:
    results_dir = REPO_ROOT / "evidence" / "guardrails"
    results_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = results_dir / f"{story_id}.json"
    payload: Dict[str, Any] = {
        "story_id": story_id,
        "passed": passed,
        "message": message,
        "guardrails_checked": guardrails_checked,
        "warnings_count": int(warnings_count or 0),
        "warnings": warnings or [],
    }

    # Optional: richer detail (MissionLog should tolerate additional fields)
    if guardrail_results is not None:
        payload["guardrail_results"] = guardrail_results

    evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f">>> Wrote guardrail evidence for {story_id} to "
        f"{evidence_path.relative_to(REPO_ROOT)}"
    )
    return evidence_path


# ---------------------------------------------------------------------------
# Story discovery + front matter access
# ---------------------------------------------------------------------------

def _extract_front_matter_block(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    return parts[1]


def _extract_scalar_from_front_matter(text: str, key: str) -> Optional[str]:
    fm = _extract_front_matter_block(text)
    if not fm:
        return None
    m = re.search(rf"^{re.escape(key)}:\s*(.+)\s*$", fm, flags=re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def find_story_file_by_id(story_id: str) -> Path:
    if not STORIES_DIR.exists():
        raise FileNotFoundError(f"Stories dir not found: {STORIES_DIR}")

    target = story_id.upper().strip()
    for path in sorted(STORIES_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        sid = _extract_scalar_from_front_matter(text, "story_id")
        if sid and sid.upper().strip() == target:
            return path

    raise FileNotFoundError(f"Story {target!r} not found under {STORIES_DIR.relative_to(REPO_ROOT)}")


def discover_non_planned_story_ids() -> List[str]:
    """
    Default run scope for demo safety:
    run guardrails only for stories that are not Planned.
    """
    ids: List[str] = []
    if not STORIES_DIR.exists():
        return ids

    for path in sorted(STORIES_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        sid = _extract_scalar_from_front_matter(text, "story_id")
        if not sid:
            continue

        overall = _extract_scalar_from_front_matter(text, "overall_status") or "Planned"
        if overall.strip().lower() != "planned":
            ids.append(sid.upper().strip())

    return ids


# ---------------------------------------------------------------------------
# Front matter updater
# ---------------------------------------------------------------------------

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
    print(
        f">>> Updated {story_file.relative_to(REPO_ROOT)} -> guardrail_adherence: {status}"
    )


# ---------------------------------------------------------------------------
# Global guardrail: G03 (LDM adherence)
# ---------------------------------------------------------------------------

def run_g03_if_applicable(story_id: str, story_file: Path) -> Tuple[bool, str, List[str], List[Dict[str, Any]]]:
    """
    Returns:
      (passed, message, guardrails_checked, guardrail_results)

    Policy:
    - If G03 is NOT declared in story front matter, it's NOT APPLICABLE -> treated as PASS.
    - If declared, run the validation logic and PASS/FAIL accordingly.
    """
    # We import the helper functions from the existing G03 script (no subprocess).
    from tools.guardrails.run_g03_ldm import (
        read_story_front_matter,
        extract_g03_config,
        resolve_contract_path,
        load_json,
        normalize_schema,
        validate_instance,
    )

    guardrails_checked: List[str] = []
    guardrail_results: List[Dict[str, Any]] = []

    try:
        front_matter = read_story_front_matter(story_file)
    except Exception as exc:
        # If we can't parse front matter, that's a guardrail framework failure.
        guardrails_checked.append("G03 (framework error)")
        return False, f"Failed to read story front matter: {exc!r}", guardrails_checked, guardrail_results

    guardrails_block = front_matter.get("guardrails", {})
    g03_decl = guardrails_block.get("G03") if isinstance(guardrails_block, dict) else None

    if not isinstance(g03_decl, dict):
        # Not applicable -> pass
        guardrails_checked.append("G03 (not applicable)")
        result = {
            "guardrail_id": "G03",
            "applicable": False,
            "passed": True,
            "message": "G03 not declared for this Story; treated as not applicable.",
            "warnings_count": 0,
            "warnings": [],
        }
        guardrail_results.append(result)
        return True, "No applicable guardrails for this Story (G03 not declared).", guardrails_checked, guardrail_results

    # Applicable: run validation
    guardrails_checked.append("G03 (LDM adherence)")

    try:
        g03 = extract_g03_config(front_matter)

        schema_path = resolve_contract_path(g03.ldm_contract, REPO_ROOT)
        schema = load_json(schema_path)

        if schema.get("$id") != g03.ldm_contract:
            raise ValueError(
                f"Schema $id mismatch: expected {g03.ldm_contract}, found {schema.get('$id')}"
            )

        schema = normalize_schema(schema, g03.mode)

        artifact_path = (
            REPO_ROOT
            / "evidence"
            / "runtime_outputs"
            / story_id
            / f"{g03.artifact}.json"
        )

        if not artifact_path.exists():
            raise FileNotFoundError(f"Runtime artifact not found: {artifact_path}")

        instance = load_json(artifact_path)
        errors = validate_instance(schema, instance)
        passed = len(errors) == 0

        result = {
            "guardrail_id": "G03",
            "applicable": True,
            "passed": passed,
            "message": "LDM validation passed" if passed else f"LDM validation failed for {g03.ldm_contract}",
            "contract_id": g03.ldm_contract,
            "artifact_path": str(artifact_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "errors": errors,
            "warnings_count": 0,
            "warnings": [],
        }
        guardrail_results.append(result)

        return passed, result["message"], guardrails_checked, guardrail_results

    except Exception as exc:
        # Applicable but evaluation failed -> fail
        result = {
            "guardrail_id": "G03",
            "applicable": True,
            "passed": False,
            "message": f"G03 evaluation error: {exc!r}",
            "warnings_count": 0,
            "warnings": [],
        }
        guardrail_results.append(result)
        return False, result["message"], guardrails_checked, guardrail_results


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_guardrails_for_story(story_id: str) -> Tuple[bool, str]:
    story_id = story_id.upper().strip()
    story_file = find_story_file_by_id(story_id)

    # MVP: run only G03 (global guardrail catalogue)
    passed, msg, checked, results = run_g03_if_applicable(story_id, story_file)

    write_guardrail_evidence(
        story_id=story_id,
        passed=passed,
        message=msg,
        guardrails_checked=checked,
        warnings=[],
        warnings_count=0,
        guardrail_results=results,
    )

    update_story_guardrail_adherence(story_file, passed)
    return passed, msg


def main(argv: List[str]) -> int:
    """
    Usage:
      python tools/run_story_guardrails.py            # run for all non-Planned Stories
      python tools/run_story_guardrails.py ST-05      # run for a single Story
    """
    if len(argv) > 1:
        requested_ids = [argv[1].upper().strip()]
    else:
        requested_ids = discover_non_planned_story_ids()

    if not requested_ids:
        print("No eligible Stories found (non-Planned). Nothing to do.")
        return 0

    overall_exit = 0
    for sid in requested_ids:
        print(f"\n=== Guardrails for Story {sid} ===")
        passed, message = run_guardrails_for_story(sid)
        print(f">>> {sid}: {'PASS' if passed else 'FAIL'} — {message}")
        if not passed:
            overall_exit = 1

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))




