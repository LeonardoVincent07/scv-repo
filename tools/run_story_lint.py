#!/usr/bin/env python
"""
Run linting for one or more Stories and update code_quality_adherence
in each Story's front matter.

MVP:
- Use Ruff to lint the Story's Python files.
- If any issues are reported, mark as fail.
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
# - lint_targets: list of Python files to lint with Ruff
STORY_CONFIG: Dict[str, Dict[str, Any]] = {
    "ST-03": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-03_map_identity_fields.md",
        "lint_targets": [
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
        "lint_targets": [
            "src/services/client_profile/service.py",
            "src/domain/models/client_profile.py",
        ],
    },
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def run_ruff_for_targets(targets: List[str]) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Run Ruff on the given Python files.

    Returns:
      (passed, message, issues)

    Where issues is a minimal list of findings (code, message, location).
    """
    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "--output-format",
        "json",
        *targets,
    ]
    print(f">>> Running Ruff: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        # Ruff not installed / importable in this environment
        return (
            False,
            f"Ruff not available: {exc!r}. Install ruff in this environment.",
            [],
        )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    if not stdout.strip():
        # No JSON output – treat as failure with diagnostic
        return (
            False,
            f"Ruff did not produce JSON output. rc={proc.returncode}, stderr={stderr.strip()}",
            [],
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return (
            False,
            f"Failed to parse Ruff JSON output: {exc!r}",
            [],
        )

    # Ruff JSON is a list of diagnostics
    issues: List[Dict[str, Any]] = []
    for diag in data:
        issues.append(
            {
                "filename": diag.get("filename"),
                "code": diag.get("code"),
                "message": diag.get("message"),
                "location": diag.get("location"),
            }
        )

    if issues:
        return (
            False,
            f"Ruff reported {len(issues)} code-quality issue(s).",
            issues,
        )

    return True, "No code-quality issues reported by Ruff.", issues


def write_lint_evidence(
    story_id: str,
    targets: List[str],
    passed: bool,
    message: str,
    issues: List[Dict[str, Any]],
) -> Path:
    """
    Write JSON evidence file for lint/code-quality adherence for this Story.
    """
    results_dir = REPO_ROOT / "evidence" / "lint"
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
    print(f">>> Wrote lint evidence for {story_id} to {evidence_path.relative_to(REPO_ROOT)}")
    return evidence_path


def update_story_code_quality_status(story_file: Path, passed: bool) -> None:
    """
    Replace the first 'code_quality_adherence: ...' line in the Story's front matter.
    """
    if not story_file.exists():
        raise FileNotFoundError(f"Story file not found: {story_file}")

    status = "pass" if passed else "fail"

    text = story_file.read_text(encoding="utf-8")

    pattern = r"(^code_quality_adherence:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(
            f"Story file {story_file} does not contain a code_quality_adherence line to update."
        )

    story_file.write_text(new_text, encoding="utf-8")
    rel = story_file.relative_to(REPO_ROOT)
    print(f">>> Updated {rel} -> code_quality_adherence: {status}")


def run_lint_for_story(story_id: str) -> Tuple[bool, str]:
    """
    Run linting for a single Story:
    - execute Ruff on its targets
    - write evidence
    - update front matter

    Returns (passed, message).
    """
    config = STORY_CONFIG[story_id]
    story_file: Path = config["story_file"]  # type: ignore[assignment]
    targets: List[str] = config["lint_targets"]  # type: ignore[assignment]

    print(f">>> Running lint/code-quality checks for Story {story_id}")
    passed, message, issues = run_ruff_for_targets(targets)

    write_lint_evidence(story_id, targets, passed, message, issues)
    update_story_code_quality_status(story_file, passed)

    status = "pass" if passed else "fail"
    print(f">>> Story {story_id} code_quality_adherence set to {status}: {message}")
    return passed, message


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    """
    Usage:
      python tools/run_story_lint.py          # run for all configured Stories
      python tools/run_story_lint.py ST-03    # run for a single Story
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
        print(f"\n=== Lint/code-quality for Story {sid} ===")
        passed, _ = run_lint_for_story(sid)
        if not passed:
            overall_exit = 1

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
