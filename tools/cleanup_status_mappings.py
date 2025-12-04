#!/usr/bin/env python
"""
Remove the accidental rollup mapping blocks:

- story_statuses: {...} from Feature files
- feature_statuses: {...} from Epic files

Run once, commit the changes, and they are gone.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _remove_block(text: str, key: str) -> str:
    """
    Remove a YAML block starting with 'key:' up to the next top-level key or EOF.

    Matches both mapping and list blocks.
    """
    pattern = rf"^{key}:\s*.*?(?=^\S|\Z)"
    return re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)


def clean_features() -> int:
    changed = 0
    for path in sorted(FEATURES_DIR.glob("*.md")):
        original = _read(path)
        updated = _remove_block(original, "story_statuses")
        if updated != original:
            # Normalise multiple blank lines left behind
            updated = re.sub(r"\n{3,}", "\n\n", updated)
            _write(path, updated)
            changed += 1
            print(f">>> Cleaned story_statuses from {path.relative_to(REPO_ROOT)}")
    return changed


def clean_epics() -> int:
    changed = 0
    for path in sorted(EPICS_DIR.glob("*.md")):
        original = _read(path)
        updated = _remove_block(original, "feature_statuses")
        if updated != original:
            updated = re.sub(r"\n{3,}", "\n\n", updated)
            _write(path, updated)
            changed += 1
            print(f">>> Cleaned feature_statuses from {path.relative_to(REPO_ROOT)}")
    return changed


def main() -> int:
    print("=== Cleaning unwanted status mapping blocks ===")
    f = clean_features()
    e = clean_epics()
    print(f"Features cleaned: {f}")
    print(f"Epics cleaned:    {e}")
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
