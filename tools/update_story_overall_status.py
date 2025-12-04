#!/usr/bin/env python
"""
Derive Story overall_status from testing / guardrail / code / security.

Rule per story:

1. Normalise each dimension:

   - pass / ok / success / compliant  -> Complete
   - fail / error / non_compliant     -> In Progress
   - not_run / pending / empty        -> Planned

2. overall_status:

   - Complete  if all four dims are Complete
   - Planned   if all four dims are Planned
   - In Progress otherwise

This script ONLY updates Story frontmatter.
Features/Epics are still rolled up by rollup_statuses.py.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


# ----------------- helpers ----------------- #

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

    # insert before last_updated if present
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + replacement + "\n" + text[start:]

    # else append at end of front matter
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def _norm_dim(raw: Optional[str]) -> str:
    """
    Normalise a dimension value to:

        Planned | In Progress | Complete
    """
    if raw is None:
        return "Planned"

    t = raw.strip().strip('"\'')
    tl = t.lower()

    # already canonical?
    if tl in {"planned"}:
        return "Planned"
    if tl in {"in progress", "in_progress", "in-progress"}:
        return "In Progress"
    if tl in {"complete", "completed"}:
        return "Complete"

    # pass-ish
    if tl in {"pass", "passed", "ok", "success", "succeeded", "compliant", "true", "yes"}:
        return "Complete"

    # fail-ish
    if tl in {"fail", "failed", "error", "non_compliant", "non-compliant", "false", "no"}:
        return "In Progress"

    # not-run / unknown → planned
    if tl in {"not_run", "not-run", "not run", "pending", "todo", "tbd", "unknown", "n/a", "na", ""}:
        return "Planned"

    # default: treat as in progress
    return "In Progress"


def _derive_overall(dim_values: List[str]) -> str:
    """
    dim_values is a list of 4 statuses (Planned/IP/Complete).

    - Complete  if all Complete
    - Planned   if all Planned
    - In Progress otherwise
    """
    s = set(dim_values)
    if s == {"Complete"}:
        return "Complete"
    if s == {"Planned"}:
        return "Planned"
    return "In Progress"


# ----------------- main ----------------- #

def update_stories() -> None:
    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue  # skip non-Mission stories

        testing = _norm_dim(_extract_scalar(text, "testing_status"))
        guardrail = _norm_dim(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _norm_dim(_extract_scalar(text, "code_quality_adherence"))
        security = _norm_dim(_extract_scalar(text, "security_policy_adherence"))

        dims = [testing, guardrail, code_quality, security]
        overall = _derive_overall(dims)

        new_text = _replace_scalar(text, "overall_status", overall)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Story {story_id}: overall_status -> {overall}")


def main() -> int:
    print("=== Deriving Story overall_status from test/guardrail/code/security ===")
    print(f"Repo root: {REPO_ROOT}")
    update_stories()
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
