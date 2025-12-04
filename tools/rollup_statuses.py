#!/usr/bin/env python
"""
Mission Control Status Roll-up (overall_status only, simple)

- Reads Story overall_status and feature mapping.
- Aggregates to Feature overall_status.
- Aggregates to Epic overall_status.
- DOES NOT touch testing / guardrail / code / security fields.

Aggregation rule (same at each level):

- Planned    if all children are Planned
- Complete   if all children are Complete
- In Progress otherwise
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"


# -------------------- helpers -------------------- #

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _extract_scalar(text: str, key: str) -> Optional[str]:
    """
    Extract 'key: value' from front matter. Returns value or None.
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


def _replace_scalar(text: str, key: str, value: str) -> str:
    """
    Replace or insert 'key: value' in the front matter.
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

    # Fallback: append at end
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def _norm_overall(raw: Optional[str]) -> str:
    """
    Normalise Story overall_status to:

        Planned | In Progress | Complete
    """
    if raw is None:
        return "Planned"

    t = raw.strip().strip('"\'')
    tl = t.lower()

    if tl in {"planned"}:
        return "Planned"
    if tl in {"in progress", "in_progress", "in-progress", "active"}:
        return "In Progress"
    if tl in {"complete", "completed", "done"}:
        return "Complete"

    # Default if unknown
    return "Planned"


def _aggregate_overall(child_statuses: List[str]) -> Optional[str]:
    """
    Roll-up:

    - Planned   if all children Planned
    - Complete  if all children Complete
    - In Progress otherwise

    Returns None if there are no children.
    """
    if not child_statuses:
        return None
    s = set(child_statuses)
    if s == {"Planned"}:
        return "Planned"
    if s == {"Complete"}:
        return "Complete"
    return "In Progress"


# -------------------- main roll-up logic -------------------- #

def collect_story_overall() -> Dict[str, Dict[str, str]]:
    """
    Return mapping: story_id -> { "feature": feature_id, "overall": overall_status }
    """
    stories: Dict[str, Dict[str, str]] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        sid = _extract_scalar(text, "story_id")
        if not sid:
            continue  # ignore legacy

        feature_id = _extract_scalar(text, "feature") or ""
        overall_raw = _extract_scalar(text, "overall_status")
        overall = _norm_overall(overall_raw)

        stories[sid] = {"feature": feature_id, "overall": overall}

    return stories


def rollup_features(stories: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    Compute overall_status per feature and write it into feature files.

    Returns mapping: feature_id -> overall_status
    """
    feature_overall: Dict[str, str] = {}

    # Build feature -> [story_ids] from stories
    feature_to_stories: Dict[str, List[str]] = {}
    for sid, info in stories.items():
        fid = info["feature"]
        if not fid:
            continue
        feature_to_stories.setdefault(fid, []).append(sid)

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)

        fid = _extract_scalar(text, "feature_id")
        if not fid:
            continue

        # Prefer explicit list in front matter if present
        listed_story_ids = _extract_yaml_list(text, "stories")
        if listed_story_ids:
            story_ids = listed_story_ids
        else:
            story_ids = feature_to_stories.get(fid, [])

        child_overall: List[str] = []
        for sid in story_ids:
            info = stories.get(sid)
            if info is None:
                child_overall.append("Planned")
            else:
                child_overall.append(info["overall"])

        agg = _aggregate_overall(child_overall)

        new_text = text
        if agg:
            new_text = _replace_scalar(new_text, "overall_status", agg)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Updated Feature {fid} overall_status -> {agg}")

        # Read back final value (may have existed already)
        final_text = _read(path)
        final_overall = _norm_overall(_extract_scalar(final_text, "overall_status"))
        feature_overall[fid] = final_overall

    return feature_overall


def rollup_epics(feature_overall: Dict[str, str]) -> None:
    """
    Compute overall_status per epic and write it into epic files.
    """
    # Build epic -> [feature_ids] from features
    epic_to_features: Dict[str, List[str]] = {}

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        fid = _extract_scalar(text, "feature_id")
        epic_id = _extract_scalar(text, "epic")
        if not fid or not epic_id:
            continue
        epic_to_features.setdefault(epic_id, []).append(fid)

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)

        eid = _extract_scalar(text, "epic_id")
        if not eid:
            continue

        feature_ids = _extract_yaml_list(text, "features")
        if not feature_ids:
            feature_ids = epic_to_features.get(eid, [])

        child_overall: List[str] = []
        for fid in feature_ids:
            child_overall.append(feature_overall.get(fid, "Planned"))

        agg = _aggregate_overall(child_overall)

        new_text = text
        if agg:
            new_text = _replace_scalar(new_text, "overall_status", agg)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Updated Epic {eid} overall_status -> {agg}")


def main() -> int:
    print("=== Mission Control Overall Status Roll-up ===")
    print(f"Repo root: {REPO_ROOT}")

    stories = collect_story_overall()
    print(f"Collected {len(stories)} stories.")

    feature_overall = rollup_features(stories)
    print(f"Rolled up {len(feature_overall)} features.")

    rollup_epics(feature_overall)
    print("Rolled up epics.")
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

