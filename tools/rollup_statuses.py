#!/usr/bin/env python
"""
Mission Control Overall Status Roll-up

Responsibilities:
- For each Story:
    - Derive overall_status from its testing / guardrail / code / security /
      halo fields (no implementation_presence).
- Aggregate Story overall_status up to Feature overall_status.
- Aggregate Feature overall_status up to Epic overall_status.

IMPORTANT:
- We ONLY ever write 'overall_status' fields.
- We NEVER touch testing_status / guardrail_adherence / code_quality_adherence /
  security_policy_adherence / halo_adherence directly; we just read them.
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
    Very simple line-based parser; assumes `key: value` is on one line.
    """
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    # strip simple quotes
    if val and val[0] in {'"', "'"} and val[-1:] == val[0]:
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


# -------------------- status helpers -------------------- #

def _norm_overall(raw: Optional[str]) -> str:
    """
    Normalise an overall_status value to:

        Planned | In Progress | Complete
    """
    if raw is None:
        return "Planned"

    t = raw.strip().strip("\"'")
    tl = t.lower()

    if tl == "planned":
        return "Planned"
    if tl in {"in progress", "in_progress", "in-progress", "active"}:
        return "In Progress"
    if tl in {"complete", "completed", "done"}:
        return "Complete"
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


def _norm_flag(raw: Optional[str]) -> str:
    """
    Normalise pass/fail/planned-ish flags used in story front matter.
    """
    if raw is None:
        return "planned"
    t = raw.strip().strip("\"'").lower()
    if t in {"pass", "passed", "ok", "true"}:
        return "pass"
    if t in {"fail", "failed", "error", "false"}:
        return "fail"
    if t in {"planned", "n/a", "na"}:
        return "planned"
    # fallback: treat unknown as planned
    return "planned"


def derive_story_overall(text: str) -> str:
    """
    Derive a Story's overall_status from its detailed fields.

    Rules:

    - If *nothing has started* (all flags 'planned')
      -> Planned
    - Else if ALL of
        testing_status, guardrail_adherence, code_quality_adherence,
        security_policy_adherence are 'pass'
      AND halo_adherence is not 'fail'
      -> Complete
    - Otherwise
      -> In Progress
    """
    testing = _norm_flag(_extract_scalar(text, "testing_status"))
    guardrail = _norm_flag(_extract_scalar(text, "guardrail_adherence"))
    code = _norm_flag(_extract_scalar(text, "code_quality_adherence"))
    security = _norm_flag(_extract_scalar(text, "security_policy_adherence"))
    halo_raw = _extract_scalar(text, "halo_adherence")
    halo = _norm_flag(halo_raw) if halo_raw is not None else "planned"

    flags = [testing, guardrail, code, security, halo]

    # 1) Nothing touched yet
    if all(f == "planned" for f in flags):
        return "Planned"

    # 2) Everything green
    if (
        testing == "pass"
        and guardrail == "pass"
        and code == "pass"
        and security == "pass"
        and halo != "fail"
    ):
        return "Complete"

    # 3) Something has happened but we are not complete
    return "In Progress"


# -------------------- main roll-up logic -------------------- #

def update_story_overall() -> Dict[str, Dict[str, str]]:
    """
    For every story file:
    - derive overall_status from detailed fields
    - write it back to the file
    - return mapping story_id -> {feature, overall}
    """
    stories: Dict[str, Dict[str, str]] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        sid = _extract_scalar(text, "story_id")
        if not sid:
            continue  # ignore legacy / non-story docs

        feature_id = _extract_scalar(text, "feature") or ""

        derived_overall = derive_story_overall(text)
        new_text = _replace_scalar(text, "overall_status", derived_overall)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Updated Story {sid} overall_status -> {derived_overall}")

        stories[sid] = {"feature": feature_id, "overall": derived_overall}

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

    stories = update_story_overall()
    print(f"Updated and collected {len(stories)} stories.")

    feature_overall = rollup_features(stories)
    print(f"Rolled up {len(feature_overall)} features.")

    rollup_epics(feature_overall)
    print("Rolled up epics.")
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
