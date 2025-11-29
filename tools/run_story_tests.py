#!/usr/bin/env python
"""
Run tests for a story and update its testing_status front-matter.

MVP: hard-wired to ST-03 and runs the full pytest suite.
If pytest exits 0 -> testing_status: pass
Else            -> testing_status: fail
"""

import subprocess
import sys
from pathlib import Path

# Paths are relative to repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
STORY_ID = "ST-03"
STORY_FILE = REPO_ROOT / "docs" / "mission_destination" / "stories" / "ST-03_map_identity_fields.md"


def run_pytest() -> int:
    """Run pytest and return exit code."""
    print(">>> Running pytest …")
    result = subprocess.run(
        ["pytest"],
        cwd=REPO_ROOT,
        check=False,
    )
    print(f">>> pytest finished with exit code {result.returncode}")
    return result.returncode


def update_testing_status(status: str) -> None:
    """Set testing_status: <status> in the story front-matter."""
    if status not in {"pass", "fail"}:
        raise ValueError(f"Invalid status {status!r}; expected 'pass' or 'fail'")

    if not STORY_FILE.exists():
        raise FileNotFoundError(f"Story file not found: {STORY_FILE}")

    lines = STORY_FILE.read_text(encoding="utf-8").splitlines()
    new_lines = []
    replaced = False

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("testing_status:"):
            indent = line[: len(line) - len(stripped)]
            new_line = f"{indent}testing_status: {status}"
            new_lines.append(new_line)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        # If for some reason the key is missing, append it just before last_updated or at end
        inserted = False
        for i, line in enumerate(new_lines):
            if line.lstrip().startswith("last_updated:"):
                new_lines.insert(i, f"testing_status: {status}")
                inserted = True
                break
        if not inserted:
            new_lines.append(f"testing_status: {status}")

    STORY_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f">>> Updated {STORY_FILE.relative_to(REPO_ROOT)} -> testing_status: {status}")


def main(argv: list[str]) -> int:
    # Optional arg e.g. ST-03; we ignore anything else for now but keep the interface
    if len(argv) > 1 and argv[1] not in {STORY_ID, STORY_ID.lower()}:
        print(f"WARNING: Only {STORY_ID} is supported in this MVP; ignoring argument {argv[1]!r}")

    exit_code = run_pytest()
    status = "pass" if exit_code == 0 else "fail"
    update_testing_status(status)
    print(f">>> Story {STORY_ID} testing_status set to {status}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
