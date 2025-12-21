#!/usr/bin/env python
"""
Normalize MissionDestination front matter and hierarchy:

1) Epics
   - Keep ONLY `overall_status` as a status field.
   - Remove other status/adherence fields (testing_status, guardrail_adherence, etc).
   - Regenerate `features:` list from Features' `epic` mappings
     (story -> feature -> epic is the golden source).

2) Features
   - Keep ONLY `overall_status` as a status field.
   - Remove other status/adherence fields and any old mapping blocks.
   - Regenerate `stories:` list from Stories' `feature` mappings.

3) Stories
   - Remove stray `status:` scalar if present (do NOT touch `overall_status`).
   - Ensure full status schema (MVP + non-MVP) exists in front matter:
       overall_status
       testing_status
       halo_adherence
       guardrail_adherence
       code_quality_adherence
       security_policy_adherence
       policy_adherence
       technology_lineage_adherence
       business_data_lineage_adherence
       self_healing_adherence
       analytics_adherence
     preserving existing values and only filling in defaults when missing.

This script is intended to be run manually:

    python tools/normalize_status_frontmatter_schema.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import re

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _extract_scalar(text: str, key: str) -> Optional[str]:
    """
    Extract 'key: value' from front matter. Returns the value or None.
    Very simple line-based parser; assumes `key: value` is on a single line.
    """
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val and val[0] in {"'", '"'} and val[-1:] == val[0]:
        val = val[1:-1]
    return val or None


def _replace_scalar(text: str, key: str, value: str) -> str:
    """
    Replace or insert 'key: value' in the front matter.

    - If the key exists, replace its first occurrence.
    - Otherwise insert before `last_updated:` if present, else append at end.
    """
    pattern = rf"^{re.escape(key)}:\s*.*$"
    replacement = f"{key}: {value}"

    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)

    # Insert before last_updated: if present
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + replacement + "\n" + text[start:]

    # Fallback: append
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def _remove_block(text: str, key: str) -> str:
    """
    Remove a scalar or YAML block starting with `key:` at the beginning of a line.

    Matches, for example:

      key: something
        child1: ...
        - list item
      <stops when a non-indented line is reached>
    """
    pattern = rf"^{re.escape(key)}:.*\n(?:^[ \t].*\n)*"
    return re.sub(pattern, "", text, flags=re.MULTILINE)


def _extract_yaml_list(text: str, key: str) -> List[str]:
    """
    Extract:

      key:
        - item1
        - item2

    Returns ['item1', 'item2'].
    """
    pattern = rf"^{re.escape(key)}:\s*\n(?P<body>(?:\s+- .*\n)+)"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return []
    body = m.group("body")
    items: List[str] = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- "):
            val = s[2:].strip()
            if val:
                items.append(val)
    return items


def _replace_yaml_list(text: str, key: str, items: List[str]) -> str:
    """
    Replace or insert a YAML list block:

      key:
        - item1
        - item2

    If `items` is empty, any existing block is removed.
    """
    block_pattern = rf"^{re.escape(key)}:\s*\n(?:\s+- .*\n)*"

    if not items:
        # Remove any existing list block for this key
        return re.sub(block_pattern, "", text, flags=re.MULTILINE)

    new_block = key + ":\n" + "".join(f"  - {item}\n" for item in items)

    if re.search(block_pattern, text, flags=re.MULTILINE):
        return re.sub(block_pattern, new_block + "\n", text, count=1, flags=re.MULTILINE)

    # Insert before overall_status if present, otherwise before last_updated,
    # otherwise append near the top.
    os_pattern = r"^overall_status:\s*.*$"
    m = re.search(os_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + new_block + "\n" + text[start:]

    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + new_block + "\n" + text[start:]

    # Fallback: append after first line of front matter
    return text + ("\n" if not text.endswith("\n") else "") + new_block + "\n"


# ---------------------------------------------------------------------------
# 1. Normalise Epics
# ---------------------------------------------------------------------------

EPIC_STATUS_KEYS_TO_REMOVE = {
    "testing_status",
    "halo_adherence",
    "guardrail_adherence",
    "code_quality_adherence",
    "security_policy_adherence",
    "feature_statuses",   # old rollup mapping
}


def normalize_epic_frontmatter() -> int:
    print(f"=== Normalising Epic front matter in {EPICS_DIR} ===")
    updated = 0

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)
        original = text

        # Strip non-overall status fields
        for key in EPIC_STATUS_KEYS_TO_REMOVE:
            text = _remove_block(text, key)

        if text != original:
            _write(path, text)
            updated += 1
            print(f"  updated {path.relative_to(REPO_ROOT)}")

    print(f"Epics updated (status cleanup): {updated}")
    return updated


# ---------------------------------------------------------------------------
# 2. Normalise Features
# ---------------------------------------------------------------------------

FEATURE_STATUS_KEYS_TO_REMOVE = {
    "testing_status",
    "halo_adherence",
    "guardrail_adherence",
    "code_quality_adherence",
    "security_policy_adherence",
    "story_statuses",     # old rollup mapping
}


def normalize_feature_frontmatter() -> int:
    print(f"=== Normalising Feature front matter in {FEATURES_DIR} ===")
    updated = 0

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        original = text

        for key in FEATURE_STATUS_KEYS_TO_REMOVE:
            text = _remove_block(text, key)

        if text != original:
            _write(path, text)
            updated += 1
            print(f"  updated {path.relative_to(REPO_ROOT)}")

    print(f"Features updated (status cleanup): {updated}")
    return updated


# ---------------------------------------------------------------------------
# 3. Normalise Stories
# ---------------------------------------------------------------------------

STORY_STATUS_DEFAULTS: Dict[str, str] = {
    # Overall status of story (Planned / In Progress / Complete)
    "overall_status": "Planned",

    # MVP status dimensions
    "testing_status": "not_run",
    # For MVP, halo is effectively defaulted to not_run
    "halo_adherence": "not_run",
    "guardrail_adherence": "not_run",
    "code_quality_adherence": "not_run",
    "security_policy_adherence": "not_run",

    # Non-MVP but part of full schema (all default 'not_run')
    "policy_adherence": "not_run",
    "technology_lineage_adherence": "not_run",
    "business_data_lineage_adherence": "not_run",
    "self_healing_adherence": "not_run",
    "analytics_adherence": "not_run",
}


def normalize_story_frontmatter() -> int:
    print(f"=== Normalising Story front matter in {STORIES_DIR} ===")
    updated = 0

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)
        original = text

        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue  # ignore non-story docs

        # Remove stray 'status:' scalar (do NOT touch overall_status)
        text = re.sub(
            r"^status:\s*.*\n",
            "",
            text,
            flags=re.MULTILINE,
        )

        # Ensure all status fields exist, do not overwrite existing values
        for key, default in STORY_STATUS_DEFAULTS.items():
            existing = _extract_scalar(text, key)
            if existing is None:
                text = _replace_scalar(text, key, default)

        if text != original:
            _write(path, text)
            updated += 1
            print(f"  updated {path.relative_to(REPO_ROOT)}")

    print(f"Stories updated (status schema + stray status): {updated}")
    return updated


# ---------------------------------------------------------------------------
# 4. Sync hierarchy lists using golden mapping
# ---------------------------------------------------------------------------

def sync_hierarchy_lists() -> None:
    """
    Make `features:` lists in Epics and `stories:` lists in Features consistent
    with the golden mapping:

        Story.frontmatter.feature  -> Feature.feature_id
        Feature.frontmatter.epic   -> Epic.epic_id
    """
    print("=== Syncing Epic.features and Feature.stories from golden mapping ===")

    # Build feature_id -> epic_id mapping and epic_id -> [feature_ids]
    feature_to_epic: Dict[str, str] = {}
    epic_to_features: Dict[str, List[str]] = {}

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        feature_id = _extract_scalar(text, "feature_id")
        epic_id = _extract_scalar(text, "epic")
        if not feature_id or not epic_id:
            continue
        feature_to_epic[feature_id] = epic_id
        epic_to_features.setdefault(epic_id, []).append(feature_id)

    # Build story_id -> feature_id mapping and feature_id -> [story_ids]
    feature_to_stories: Dict[str, List[str]] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)
        story_id = _extract_scalar(text, "story_id")
        feature_id = _extract_scalar(text, "feature")
        if not story_id or not feature_id:
            continue
        feature_to_stories.setdefault(feature_id, []).append(story_id)

    # Normalise ordering
    for eid, lst in epic_to_features.items():
        epic_to_features[eid] = sorted(set(lst))
    for fid, lst in feature_to_stories.items():
        feature_to_stories[fid] = sorted(set(lst))

    # Update Epics: features list
    epic_updates = 0
    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)
        original = text

        epic_id = _extract_scalar(text, "epic_id")
        if not epic_id:
            continue

        features_list = epic_to_features.get(epic_id, [])
        text = _replace_yaml_list(text, "features", features_list)

        if text != original:
            _write(path, text)
            epic_updates += 1
            print(f"  synced features list for epic {epic_id} ({path.relative_to(REPO_ROOT)})")

    # Update Features: stories list
    feature_updates = 0
    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        original = text

        feature_id = _extract_scalar(text, "feature_id")
        if not feature_id:
            continue

        stories_list = feature_to_stories.get(feature_id, [])
        text = _replace_yaml_list(text, "stories", stories_list)

        if text != original:
            _write(path, text)
            feature_updates += 1
            print(f"  synced stories list for feature {feature_id} ({path.relative_to(REPO_ROOT)})")

    print(f"Hierarchy sync complete: epics_updated={epic_updates}, features_updated={feature_updates}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Normalising MissionDestination front matter & hierarchy ===")
    print(f"Repo root: {REPO_ROOT}")

    normalize_epic_frontmatter()
    normalize_feature_frontmatter()
    normalize_story_frontmatter()
    sync_hierarchy_lists()

    print("=== Done normalising ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
