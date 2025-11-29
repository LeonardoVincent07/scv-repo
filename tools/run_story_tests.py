#!/usr/bin/env python3
import subprocess
from pathlib import Path
import re
import sys

# Adjust this if your repo root is different
REPO_ROOT = Path(__file__).resolve().parents[1]

# Where your story markdown files live
STORY_DIRS = [
    REPO_ROOT / "docs" / "mission_destination" / "stories",
]

# Mapping from story_id -> list of test paths (relative to repo root)
STORY_TEST_MAP = {
    "ST-03": [
        Path("tests/services/client_profile/test_client_profile_service.py"),
    ],
    # Add more mappings here as you wire more stories to tests
}


def find_story_files() -> list[Path]:
    files: list[Path] = []
    for d in STORY_DIRS:
        if d.exists():
            files.extend(d.rglob("*.md"))
    return files


def extract_story_id(text: str) -> str | None:
    """
    Look for a line like: story_id: ST-03
    anywhere in the file.
    """
    m = re.search(r"^story_id:\s*(\S+)", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else None


def update_testing_status(story_path: Path, text: str, status: str) -> None:
    """
    Replace the first 'testing_status:' line with the new status.
    """
    if status not in {"not_run", "pass", "fail"}:
        raise ValueError(f"Invalid testing_status: {status}")

    pattern = r"(^testing_status:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        print(f"[WARN] No testing_status line found in {story_path}, leaving unchanged")
        return

    story_path.write_text(new_text, encoding="utf-8")
    print(f"[{story_path.name}] testing_status -> {status}")


def run_pytest_for_story(story_id: str) -> int | None:
    """
    Run pytest for all tests mapped to this story_id.

    Returns:
      0    -> all mapped tests passed
      >0   -> at least one mapped test failed
      None -> no mapped tests for this story_id
    """
    test_paths = STORY_TEST_MAP.get(story_id)
    if not test_paths:
        print(f"[{story_id}] No mapped tests, skipping (status stays as-is)")
        return None

    overall_rc = 0
    for rel_path in test_paths:
        abs_path = REPO_ROOT / rel_path
        if not abs_path.exists():
            print(f"[WARN] {story_id}: mapped test file {abs_path} does not exist")
            overall_rc = 1
            continue

        print(f"[{story_id}] Running pytest on {rel_path}")
        result = subprocess.run(
             [sys.executable, "-m", "pytest", str(abs_path)],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            overall_rc = result.returncode

    return overall_rc


def main() -> None:
    story_files = find_story_files()
    if not story_files:
        print("No story files found.")
        sys.exit(1)

    for story_path in story_files:
        text = story_path.read_text(encoding="utf-8")
        story_id = extract_story_id(text)

        if not story_id:
            print(f"[{story_path}] No story_id found, skipping")
            continue

        rc = run_pytest_for_story(story_id)

        if rc is None:
            # No tests mapped for this story; leave testing_status as-is (likely 'not_run')
            continue

        status = "pass" if rc == 0 else "fail"
        update_testing_status(story_path, text, status)


if __name__ == "__main__":
    main()
