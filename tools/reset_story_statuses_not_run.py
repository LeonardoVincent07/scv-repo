#!/usr/bin/env python
"""
Reset ALL Story status/adherence dimensions to 'not_run' across MissionDestination.

Scope: docs/mission_destination/stories/*.md only
Edits: YAML front matter only (between first two '---' lines)

Fields reset:
- testing_status
- halo_adherence
- guardrail_adherence
- code_quality_adherence
- security_policy_adherence
- policy_adherence
- technology_lineage_adherence
- business_data_lineage_adherence
- self_healing_adherence
- analytics_adherence

Also sets overall_status to Planned (consistent with roll-up normalisation rules).
We do NOT touch Features/Epics here; rollup_statuses.py will handle those.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"

RESET_KEYS: Dict[str, str] = {
    "testing_status": "not_run",
    "halo_adherence": "not_run",
    "guardrail_adherence": "not_run",
    "code_quality_adherence": "not_run",
    "security_policy_adherence": "not_run",
    "policy_adherence": "not_run",
    "technology_lineage_adherence": "not_run",
    "business_data_lineage_adherence": "not_run",
    "self_healing_adherence": "not_run",
    "analytics_adherence": "not_run",
}

def split_front_matter(text: str) -> Tuple[str, str, str]:
    """
    Returns (fm, body_prefix, body) where:
      fm = front matter including the wrapping --- lines
      body_prefix = "" (kept for clarity)
      body = rest of doc
    If no front matter found, returns ("", "", original_text).
    """
    # front matter must start at beginning
    if not text.startswith("---"):
        return "", "", text

    # find second --- on its own line
    m = re.search(r"^---\s*$", text, flags=re.MULTILINE)
    if not m:
        return "", "", text

    # first delimiter is at pos 0; find the next delimiter after first line
    m2 = re.search(r"^---\s*$", text[m.end():], flags=re.MULTILINE)
    if not m2:
        return "", "", text

    end = m.end() + m2.end()
    fm = text[:end]
    body = text[end:]
    return fm, "", body

def replace_or_insert_scalar(fm: str, key: str, value: str) -> str:
    """
    Replace first occurrence of '^key: ...' in front matter.
    If missing, insert before 'last_updated:' if present, else append before closing '---'.
    """
    pattern = rf"^(?P<k>{re.escape(key)}:\s*).*$"
    if re.search(pattern, fm, flags=re.MULTILINE):
        return re.sub(pattern, rf"\g<k>{value}", fm, count=1, flags=re.MULTILINE)

    # insert before last_updated if present
    lu = re.search(r"^last_updated:\s*.*$", fm, flags=re.MULTILINE)
    insertion = f"{key}: {value}\n"
    if lu:
        return fm[: lu.start()] + insertion + fm[lu.start():]

    # otherwise insert just before the closing '---' (the second delimiter)
    parts = fm.splitlines(True)
    # find last line that is '---'
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].strip() == "---":
            parts.insert(i, insertion)
            return "".join(parts)

    # fallback: append
    if not fm.endswith("\n"):
        fm += "\n"
    return fm + insertion

def main() -> int:
    if not STORIES_DIR.exists():
        print(f"ERROR: Stories dir not found: {STORIES_DIR}")
        return 1

    updated = 0
    scanned = 0

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, _, body = split_front_matter(text)
        if not fm:
            continue

        # only touch real stories
        if not re.search(r"^story_id:\s*.+$", fm, flags=re.MULTILINE):
            continue

        scanned += 1
        new_fm = fm

        # Force baseline overall_status (roll-up maps not_run dims -> Planned anyway)
        new_fm = replace_or_insert_scalar(new_fm, "overall_status", "Planned")

        for k, v in RESET_KEYS.items():
            new_fm = replace_or_insert_scalar(new_fm, k, v)

        new_text = new_fm + body
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
            rel = path.relative_to(REPO_ROOT)
            print(f"updated {rel}")

    print(f"\nDone. Scanned stories: {scanned}, Updated: {updated}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
