#!/usr/bin/env python
"""
Mission Control Status Schema Audit

Reads epics, features, and stories under:

  docs/mission_destination/epics
  docs/mission_destination/features
  docs/mission_destination/stories

and reports any items that are *not* in the standard MissionDestination shape.

We check:

EPICS
  - missing epic_id
  - missing features list
  - epic_id referenced by no features (informational)

FEATURES
  - missing feature_id
  - missing epic
  - missing stories list
  - epic reference that does not exist

STORIES
  - missing story_id
  - missing feature
  - feature reference that does not exist

This script is READ-ONLY: it does not change any files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


REPO_ROOT = Path(__file__).resolve().parents[1]
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_scalar(text: str, key: str) -> Optional[str]:
    """
    Extract 'key: value' from front matter. Returns the value or None.
    """
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val and val[0] in {"'", '"'} and val[-1:] == val[0]:
        val = val[1:-1]
    return val or None


def _extract_yaml_list(text: str, key: str) -> List[str]:
    """
    Extract:

      key:
        - item1
        - item2

    Returns [item1, item2].
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


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EpicInfo:
    path: Path
    epic_id: Optional[str]
    features: List[str]


@dataclass
class FeatureInfo:
    path: Path
    feature_id: Optional[str]
    epic: Optional[str]
    stories: List[str]


@dataclass
class StoryInfo:
    path: Path
    story_id: Optional[str]
    feature: Optional[str]


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------

def collect_epics() -> Dict[str, EpicInfo]:
    epics: Dict[str, EpicInfo] = {}
    print(f"Scanning epics in {EPICS_DIR}...")

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)
        epic_id = _extract_scalar(text, "epic_id")
        features = _extract_yaml_list(text, "features")

        key = epic_id if epic_id else f"__NO_ID__:{path.name}"
        epics[key] = EpicInfo(path=path, epic_id=epic_id, features=features)

    return epics


def collect_features() -> Dict[str, FeatureInfo]:
    features: Dict[str, FeatureInfo] = {}
    print(f"Scanning features in {FEATURES_DIR}...")

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        feature_id = _extract_scalar(text, "feature_id")
        epic = _extract_scalar(text, "epic")
        stories = _extract_yaml_list(text, "stories")

        key = feature_id if feature_id else f"__NO_ID__:{path.name}"
        features[key] = FeatureInfo(
            path=path,
            feature_id=feature_id,
            epic=epic,
            stories=stories,
        )

    return features


def collect_stories() -> Dict[str, StoryInfo]:
    stories: Dict[str, StoryInfo] = {}
    print(f"Scanning stories in {STORIES_DIR}...")

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)
        story_id = _extract_scalar(text, "story_id")
        feature = _extract_scalar(text, "feature")

        key = story_id if story_id else f"__NO_ID__:{path.name}"
        stories[key] = StoryInfo(path=path, story_id=story_id, feature=feature)

    return stories


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def audit_schema() -> None:
    epics = collect_epics()
    features = collect_features()
    stories = collect_stories()

    epic_ids: Set[str] = {e.epic_id for e in epics.values() if e.epic_id}
    feature_ids: Set[str] = {f.feature_id for f in features.values() if f.feature_id}

    problems: List[str] = []

    # --- Epics ---
    problems.append("\n=== EPICS ===")

    missing_epic_id = [
        e for e in epics.values() if e.epic_id is None
    ]
    if missing_epic_id:
        problems.append("Epics missing epic_id:")
        for e in missing_epic_id:
            problems.append(f"  - {e.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All epics have epic_id.")

    missing_features_list = [
        e for e in epics.values() if e.epic_id and not e.features
    ]
    if missing_features_list:
        problems.append("Epics with no features list defined:")
        for e in missing_features_list:
            problems.append(f"  - {e.epic_id}: {e.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All epics with epic_id have a features list (may be empty).")

    # Epics that are never referenced by any feature (informational)
    referenced_epics: Set[str] = {
        f.epic for f in features.values() if f.epic is not None
    }
    unreferenced_epics = sorted(epic_ids - referenced_epics)
    problems.append("Epics with epic_id that are not referenced by any feature:")
    if unreferenced_epics:
        for eid in unreferenced_epics:
            ep = [e for e in epics.values() if e.epic_id == eid][0]
            problems.append(f"  - {eid}: {ep.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("  (none)")

    # --- Features ---
    problems.append("\n=== FEATURES ===")

    missing_feature_id = [
        f for f in features.values() if f.feature_id is None
    ]
    if missing_feature_id:
        problems.append("Features missing feature_id:")
        for f in missing_feature_id:
            problems.append(f"  - {f.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All features have feature_id.")

    missing_epic_ref = [
        f for f in features.values() if f.feature_id and f.epic is None
    ]
    if missing_epic_ref:
        problems.append("Features with feature_id but no epic reference:")
        for f in missing_epic_ref:
            problems.append(f"  - {f.feature_id}: {f.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All features with feature_id have an epic reference.")

    missing_stories_list = [
        f for f in features.values() if f.feature_id and not f.stories
    ]
    if missing_stories_list:
        problems.append("Features with feature_id but no stories list defined:")
        for f in missing_stories_list:
            problems.append(f"  - {f.feature_id}: {f.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All features with feature_id have a stories list (may be empty).")

    bad_epic_ref = [
        f for f in features.values()
        if f.feature_id and f.epic and f.epic not in epic_ids
    ]
    if bad_epic_ref:
        problems.append("Features referencing an epic that does not exist:")
        for f in bad_epic_ref:
            problems.append(
                f"  - {f.feature_id} -> epic '{f.epic}' (missing), file: {f.path.relative_to(REPO_ROOT)}"
            )
    else:
        problems.append("No features reference missing epics.")

    # --- Stories ---
    problems.append("\n=== STORIES ===")

    missing_story_id = [
        s for s in stories.values() if s.story_id is None
    ]
    if missing_story_id:
        problems.append("Stories missing story_id:")
        for s in missing_story_id:
            problems.append(f"  - {s.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All stories have story_id.")

    missing_feature_ref = [
        s for s in stories.values() if s.story_id and s.feature is None
    ]
    if missing_feature_ref:
        problems.append("Stories with story_id but no feature reference:")
        for s in missing_feature_ref:
            problems.append(f"  - {s.story_id}: {s.path.relative_to(REPO_ROOT)}")
    else:
        problems.append("All stories with story_id have a feature reference.")

    bad_feature_ref = [
        s for s in stories.values()
        if s.story_id and s.feature and s.feature not in feature_ids
    ]
    if bad_feature_ref:
        problems.append("Stories referencing a feature that does not exist:")
        for s in bad_feature_ref:
            problems.append(
                f"  - {s.story_id} -> feature '{s.feature}' (missing), file: {s.path.relative_to(REPO_ROOT)}"
            )
    else:
        problems.append("No stories reference missing features.")

    # -----------------------------------------------------------------------
    # Print report
    # -----------------------------------------------------------------------
    print("\n".join(problems))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Mission Control Status Schema Audit ===")
    print(f"Repo root: {REPO_ROOT}")
    audit_schema()
    print("\n=== Audit complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
