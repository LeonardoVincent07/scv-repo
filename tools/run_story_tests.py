#!/usr/bin/env python
"""
Run tests for one or more Stories, record results, and update testing_status
in each Story's front-matter.

For each Story:
- Run pytest on its configured targets
- Write evidence to evidence/test_results/<ST-XX>.json
- Update testing_status: pass|fail in the Story markdown front matter
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Repo root = parent of /tools
REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Story configuration
# ---------------------------------------------------------------------------

# As more Stories gain real tests, add them here.
STORY_CONFIG: Dict[str, Dict[str, object]] = {
    "ST-03": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-03_map_identity_fields.md",
        # Pytest targets for this Story (should only contain tests for ST-03)
        "pytest_targets": [
            "tests/services/client_profile/test_client_profile_service.py",
        ],
    },
    "ST-04": {
        "story_file": REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-04_map_identifiers.md",
        # Separate test file focused on identifier behaviour for ST-04
        "pytest_targets": [
            "tests/services/client_profile/test_st_04_map_identifiers.py",
        ],
    },
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def run_pytest_for_story(story_id: str, pytest_targets: List[str]) -> int:
    """
    Run pytest for the given Story and return its exit code.

    Uses `sys.executable -m pytest` so it works reliably on Windows, Mac, Linux.
    """
    cmd = [sys.executable, "-m", "pytest", "-q", *pytest_targets]
    print(f">>> Running tests for {story_id}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
    print(f">>> {story_id} pytest exit code: {result.returncode}")
    return result.returncode


def write_test_result_evidence(
    story_id: str,
    pytest_targets: List[str],
    exit_code: int,
    status: str,
) -> Path:
    """
    Write a small JSON evidence file with the Story's test result.
    """
    results_dir = REPO_ROOT / "evidence" / "test_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = results_dir / f"{story_id}.json"
    payload = {
        "story_id": story_id,
        "pytest_targets": pytest_targets,
        "exit_code": exit_code,
        "status": status,
    }
    evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        ">>> Wrote test evidence for "
        f"{story_id} to {evidence_path.relative_to(REPO_ROOT)}"
    )
    return evidence_path


def update_story_testing_status(story_file: Path, status: str) -> None:
    """
    Replace the first 'testing_status: ...' line in the Story's front-matter.
    """
    if status not in {"pass", "fail"}:
        raise ValueError(f"Invalid status {status!r}; expected 'pass' or 'fail'")

    if not story_file.exists():
        raise FileNotFoundError(f"Story file not found: {story_file}")

    text = story_file.read_text(encoding="utf-8")

    pattern = r"(^testing_status:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        raise RuntimeError(
            f"Story file {story_file} does not contain a testing_status line to update."
        )

    story_file.write_text(new_text, encoding="utf-8")
    rel = story_file.relative_to(REPO_ROOT)
    print(f">>> Updated {rel} -> testing_status: {status}")


def run_for_story(story_id: str) -> Tuple[int, str]:
    """
    Execute end-to-end for a single Story:
    - run pytest on its configured targets
    - derive status
    - write evidence
    - update front matter

    Returns (exit_code, status).
    """
    config = STORY_CONFIG[story_id]
    story_file: Path = config["story_file"]  # type: ignore[assignment]
    pytest_targets: List[str] = config["pytest_targets"]  # type: ignore[assignment]

    exit_code = run_pytest_for_story(story_id, pytest_targets)
    status = "pass" if exit_code == 0 else "fail"

    write_test_result_evidence(story_id, pytest_targets, exit_code, status)
    update_story_testing_status(story_file, status)

    print(f">>> Story {story_id} testing_status set to {status}")
    return exit_code, status


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    """
    Usage:
      python tools/run_story_tests.py          # run for all configured Stories
      python tools/run_story_tests.py ST-03    # run for a single Story
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
        print(f"\n=== Running tests for Story {sid} ===")
        exit_code, _ = run_for_story(sid)
        overall_exit = max(overall_exit, exit_code)

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

