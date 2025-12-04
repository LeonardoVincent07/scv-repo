#!/usr/bin/env python
"""
Reset all MissionDestination Story overall_status to 'Planned'.

We will then manually update a small number of stories to 'In Progress'
or 'Complete' and let rollup_statuses.py aggregate from there.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _extract_scalar(text: str, key: str) -> Optional[str]:
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val and val[0] in {"'", '"'} and val[-1:] == val[0]:
        val = val[1:-1]
    return val or None


def _replace_scalar(text: str, key: str, value: str) -> str:
    pattern = rf"^{re.escape(key)}:\s*.*$"
    replacement = f"{key}: {value}"

    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)

    # insert before last_updated: if present
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + replacement + "\n" + text[start:]

    # else append at end
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def main() -> int:
    print("=== Resetting Story overall_status to Planned ===")
    print(f"Stories dir: {STORIES_DIR}")

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)
        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue

        new_text = _replace_scalar(text, "overall_status", "Planned")
        if new_text != text:
            _write(path, new_text)
            print(f">>> {story_id}: overall_status -> Planned")

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
