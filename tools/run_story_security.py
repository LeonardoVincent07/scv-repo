#!/usr/bin/env python
"""
Run security checks for one or more Stories and update security_policy_adherence
in each Story's front matter.

MVP:
- Use Bandit to scan the Story's Python files for security issues.
- If any Medium/High severity issues are found, mark as fail.
- Otherwise mark as pass.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Repo root + sys.path
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Story configuration
# ---------------------------------------------------------------------------

# For each Story:
# - story_file: markdown Story file
# - security_targets: list of Python files to scan with Bandit
STORY_CONFIG: Dict[str, Dict[str, Any]] = {
    "ST-03": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-03_map_identity_fields.md",
        "security_targets": [
            "src/services/client_profile/service.py",
            "src/domain/models/client_profile.py",
        ],
    },
    "ST-04": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-04_map_identifiers.md",
        "security_targets": [
            "src/services/client_profile/service.py",
            "src/domain/models/client_profile.py",
        ],
    },
    "ST-20": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-20_assemble_base_profile.md",
        "security_targets": [
            "src/services/client_profile/service.py",
            "src/domain/models/client_profile.py",
        ],
    },
    "ST-30": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-30_audit_ingestion.md",
        "security_targets": [
            "src/services/audit/service.py",
        ],
    },
     "ST-00": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-00-backend-api-availability.md",
        "security_targets": [
            "app_backend/main.py",
        ],
    },

}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def run_bandit_for_targets(targets: List[str]) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Run Bandit on the given Python files.

    Returns:
      (passed, message, issues)

    Where issues is a minimal list of findings we care about.
    """
    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-q",        # quiet banner
        "-f",
        "json",      # JSON output
        "-o",
        "-",         # write JSON to stdout
        *targets,
    ]
    print(f">>> Running Bandit: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        # bandit not installed / not importable
        return (
            False,
            f"Bandit not available: {exc!r}. Install bandit in this environment.",
            [],
        )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    # Bandit often returns 0 when no issues, 1 when issues found.
    # We don't rely solely on returncode; we parse JSON.
    if not stdout.strip():
        return (
            False,
            f"Bandit did not produce JSON output. rc={proc.returncode}, stderr={stderr.strip()}",
            [],
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return (
            False,
            f"Failed to parse Bandit JSON output: {exc!r}",
            [],
        )

    raw_results = data.get("results", []) or []

    # Keep only medium/high severity & confidence findings.
    issues: List[Dict[str, Any]] = []
    for r in raw_results:
        severity = (r.get("issue_severity") or "").upper()
        confidence = (r.get("issue_confidence") or "").upper()
        if severity in {"MEDIUM", "HIGH"} and confidence in {"MEDIUM", "HIGH"}:
            issues.append(
                {
                    "filename": r.get("filename"),
                    "line_number": r.get("line_number"),
                    "test_id": r.get("test_id"),
                    "issue_severity": severity,
                    "issue_confidence": confidence,
                    "issue_text": r.get("issue_text"),
                }
            )

    if issues:
        return (
            False,
            f"Bandit found {len(issues)} medium/high security issue(s).",
            issues,
        )

    return True, "No medium/high security issues found by Bandit.", issues


def write_security_evidence(
    story_id: str,
    targets: List[str],
    passed: bool,
    message: str,
    issues: List[Dict[str, Any]],
) -> Path:
    """
    Write JSON evidence file for security adherence for this Story.
    """
    results_dir = REPO_ROOT / "evidence" / "security"
    results_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = results_dir / f"{story_id}.json"
    payload = {
        "story_id": story_id,
        "targets": targets,
        "passed": passed,
        "message": message,
        "issues": issues,
    }
    evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f">>> Wrote security evidence for {story_id} to {evidence_path.relative_to(REPO_ROOT)}")
    return evidence_path


def update_story_security_status(story_file: Path, passed: bool) -> None:
    """
    Replace the first 'security_policy_adherence: ...' line in the Story's front matter.
    """
    if not story_file.exists():
        raise FileNotFoundError(f"Story file not found: {story_file}")

    status = "pass" if passed else "fail"

    text = story_file.read_text(encoding="utf-8")

    pattern = r"(^security_policy_adherence:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(
            f"Story file {story_file} does not contain a security_policy_adherence line to update."
        )

    story_file.write_text(new_text, encoding="utf-8")
    rel = story_file.relative_to(REPO_ROOT)
    print(f">>> Updated {rel} -> security_policy_adherence: {status}")


def run_security_for_story(story_id: str) -> Tuple[bool, str]:
    """
    Run security scan for a single Story:
    - execute Bandit on its targets
    - write evidence
    - update front matter

    Returns (passed, message).
    """
    config = STORY_CONFIG[story_id]
    story_file: Path = config["story_file"]  # type: ignore[assignment]
    targets: List[str] = config["security_targets"]  # type: ignore[assignment]

    print(f">>> Running security checks for Story {story_id}")
    passed, message, issues = run_bandit_for_targets(targets)

    write_security_evidence(story_id, targets, passed, message, issues)
    update_story_security_status(story_file, passed)

    status = "pass" if passed else "fail"
    print(f">>> Story {story_id} security_policy_adherence set to {status}: {message}")
    return passed, message


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    """
    Usage:
      python tools/run_story_security.py          # run for all configured Stories
      python tools/run_story_security.py ST-03    # run for a single Story
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
        print(f"\n=== Security for Story {sid} ===")
        passed, _ = run_security_for_story(sid)
        if not passed:
            overall_exit = 1

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
