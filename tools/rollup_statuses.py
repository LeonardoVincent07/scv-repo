#!/usr/bin/env python
"""
Roll up Story statuses into Features and Epics.

- Reads Story front matter (docs/mission_destination/stories/*.md)
- Aggregates per-Feature Story overall_status into:
    - feature.overall_status
    - feature.story_statuses: { ST-XX: Planned|In Progress|Complete }
- Aggregates per-Epic Feature overall_status into:
    - epic.overall_status
    - epic.feature_statuses: { FT-YY: Planned|In Progress|Complete }

We deliberately:
- Do NOT touch Story files (Stories remain the atomic ground truth).
- Keep per-dimension fields on Features/Epics as literal "aggregated"
  (per mission_control_status_model).
- Use only the existing front matter + Mission Control rules.

MVP rules:

Story overall_status source:
- Prefer `overall_status:` in Story front matter if present.
- Otherwise, fall back to `status:` (e.g. "in_progress") and map to:
    planned      -> Planned
    in_progress  -> In Progress
    in-progress  -> In Progress
    active       -> In Progress
    done/complete-> Complete
- If nothing found, default to Planned.

Feature overall_status:
- If no Stories listed: leave existing overall_status as-is.
- Else:
    - All child Stories Planned        -> Planned
    - All child Stories Complete       -> Complete
    - Otherwise                        -> In Progress

Epic overall_status:
- If no Features listed: leave existing overall_status as-is.
- Else:
    - All child Features Planned       -> Planned
    - All child Features Complete      -> Complete
    - Otherwise                        -> In Progress
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"


# ---------------------------------------------------------------------------
# Helpers: extract simple scalars and YAML list blocks via regex
# ---------------------------------------------------------------------------

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _extract_scalar(text: str, key: str) -> str | None:
    """
    Extract simple 'key: value' scalars from front matter.
    Returns the stripped value or None if not found.
    """
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    value = m.group(1).strip()
    # Strip YAML quotes if present
    if value and value[0] in {'"', "'"} and value[-1:] == value[0]:
        value = value[1:-1]
    return value


def _extract_yaml_list(text: str, key: str) -> List[str]:
    """
    Extract a simple YAML list:

    key:
      - ITEM1
      - ITEM2

    Returns [ITEM1, ITEM2]. If key not found, returns [].
    """
    pattern = rf"^{re.escape(key)}:\s*\n(?P<body>(?:\s+- .*\n)+)"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return []

    body = m.group("body")
    items: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if item:
                items.append(item)
    return items


def _replace_scalar(text: str, key: str, value: str) -> str:
    """
    Replace or insert a simple scalar `key: value`.

    - If 'key:' exists, replace that line.
    - Otherwise, insert it before 'last_updated:' if present,
      else append near the end of the front matter.
    """
    pattern = rf"^{re.escape(key)}:\s*.*$"
    replacement = f"{key}: {value}"

    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)

    # Try to insert before last_updated:
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + replacement + "\n" + text[start:]

    # Fallback: append at end
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def _replace_mapping_block(text: str, key: str, mapping: Dict[str, str]) -> str:
    """
    Replace or insert a YAML mapping block, e.g.:

    key:
      A: Planned
      B: In Progress

    - If an existing block starting with 'key:' is found, replace it.
    - Otherwise, insert before 'last_updated:' if present, else append.

    Mapping entries are written in sorted key order for determinism.
    """
    if not mapping:
        # If no entries, keep an empty mapping for clarity
        block = f"{key}: {{}}"
    else:
        lines = [f"{key}:"]
        for k in sorted(mapping.keys()):
            v = mapping[k]
            lines.append(f"  {k}: {v}")
        block = "\n".join(lines)

    pattern = rf"^{re.escape(key)}:.*?(?=^\S|\Z)"
    flags = re.MULTILINE | re.DOTALL

    if re.search(pattern, text, flags=flags):
        return re.sub(pattern, block + "\n", text, count=1, flags=flags)

    # Insert before last_updated:
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + block + "\n\n" + text[start:]

    # Fallback: append at end
    if not text.endswith("\n"):
        text += "\n"
    return text + block + "\n"


# ---------------------------------------------------------------------------
# Status aggregation logic
# ---------------------------------------------------------------------------

def _normalise_story_overall_status(raw_overall: str | None, raw_status: str | None) -> str:
    """
    Map the Story's status fields to canonical:
      Planned | In Progress | Complete

    Priority:
    - If overall_status present, trust it.
    - Else, derive from 'status:' if present.
    - Else, Planned.
    """
    if raw_overall:
        return raw_overall.strip()

    if raw_status:
        val = raw_status.strip().strip('"\'').lower()
        if val in {"planned"}:
            return "Planned"
        if val in {"in_progress", "in-progress", "active"}:
            return "In Progress"
        if val in {"done", "complete", "completed"}:
            return "Complete"

    return "Planned"


def _aggregate_overall(child_statuses: List[str]) -> str:
    """
    Mission Control aggregation:

    - Planned   if all children are Planned
    - Complete  if all children are Complete
    - In Progress otherwise
    """
    if not child_statuses:
        # Caller decides how to handle "no children" – we won't override.
        return ""

    vals = set(child_statuses)
    if vals == {"Planned"}:
        return "Planned"
    if vals == {"Complete"}:
        return "Complete"
    return "In Progress"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class StoryInfo:
    story_id: str
    feature_id: str | None
    overall_status: str


@dataclass
class FeatureInfo:
    feature_id: str
    epic_id: str | None
    stories: List[str]
    overall_status: str


# ---------------------------------------------------------------------------
# Collection functions
# ---------------------------------------------------------------------------

def collect_story_infos() -> Dict[str, StoryInfo]:
    """Scan all Story files and collect StoryInfo keyed by story_id."""
    story_infos: Dict[str, StoryInfo] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read_text(path)

        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            # Non-standard Story doc (e.g. older UI story); skip for Mission Control
            continue

        feature_id = _extract_scalar(text, "feature")
        raw_overall = _extract_scalar(text, "overall_status")
        raw_status = _extract_scalar(text, "status")

        overall = _normalise_story_overall_status(raw_overall, raw_status)

        story_infos[story_id] = StoryInfo(
            story_id=story_id,
            feature_id=feature_id,
            overall_status=overall,
        )

    return story_infos


def collect_feature_infos(story_infos: Dict[str, StoryInfo]) -> Dict[str, FeatureInfo]:
    """Scan Feature files, compute per-feature story_statuses and overall_status."""

    feature_infos: Dict[str, FeatureInfo] = {}

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read_text(path)

        feature_id = _extract_scalar(text, "feature_id")
        if not feature_id:
            # Non-MissionDestination feature (e.g. older UI format); skip
            continue

        epic_id = _extract_scalar(text, "epic")
        story_ids = _extract_yaml_list(text, "stories")

        # Build story_statuses mapping for this feature
        story_statuses: Dict[str, str] = {}
        for sid in story_ids:
            info = story_infos.get(sid)
            if info is not None:
                story_statuses[sid] = info.overall_status
            else:
                # Story file missing or non-standard – assume Planned
                story_statuses[sid] = "Planned"

        # Compute aggregated feature overall_status
        child_statuses = list(story_statuses.values())
        if child_statuses:
            agg = _aggregate_overall(child_statuses)
        else:
            # No children – keep existing value (we'll read then write only if agg non-empty)
            agg = ""

        # Update front matter in text
        new_text = text

        if agg:
            new_text = _replace_scalar(new_text, "overall_status", agg)

        new_text = _replace_mapping_block(new_text, "story_statuses", story_statuses)

        if new_text != text:
            _write_text(path, new_text)
            rel = path.relative_to(REPO_ROOT)
            print(f">>> Updated {rel} (Feature {feature_id})")

        # Read back the (possibly updated) overall_status for Epic-level aggregation
        final_text = _read_text(path)
        final_overall = _extract_scalar(final_text, "overall_status") or "Planned"

        feature_infos[feature_id] = FeatureInfo(
            feature_id=feature_id,
            epic_id=epic_id,
            stories=story_ids,
            overall_status=final_overall,
        )

    return feature_infos


def update_epics(feature_infos: Dict[str, FeatureInfo]) -> None:
    """Scan Epics, compute feature_statuses and overall_status, and write back."""

    # Build lookup: epic_id -> { feature_id: overall_status }
    epic_child_statuses: Dict[str, Dict[str, str]] = {}

    for f in feature_infos.values():
        if not f.epic_id:
            continue
        epic_child_statuses.setdefault(f.epic_id, {})[f.feature_id] = f.overall_status

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read_text(path)

        epic_id = _extract_scalar(text, "epic_id")
        if not epic_id:
            # Non-MissionDestination epic (e.g. older UI epic); skip
            continue

        child_map = epic_child_statuses.get(epic_id, {})
        child_statuses = list(child_map.values())

        new_text = text

        if child_statuses:
            agg = _aggregate_overall(child_statuses)
            if agg:
                new_text = _replace_scalar(new_text, "overall_status", agg)

        new_text = _replace_mapping_block(new_text, "feature_statuses", child_map)

        if new_text != text:
            _write_text(path, new_text)
            rel = path.relative_to(REPO_ROOT)
            print(f">>> Updated {rel} (Epic {epic_id})")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Mission Control Status Roll-up ===")
    print(f"Repo root: {REPO_ROOT}")

    stories = collect_story_infos()
    print(f"Found {len(stories)} Stories with Mission Control front matter.")

    features = collect_feature_infos(stories)
    print(f"Updated {len(features)} Features with story_statuses and overall_status.")

    update_epics(features)
    print("Updated Epics with feature_statuses and overall_status.")

    print("=== Roll-up complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

