#!/usr/bin/env python
"""
Mission Control Overall Status Roll-up

Responsibilities:
- For each Story:
    - Derive overall_status from its testing / halo / guardrail /
      code-quality / security fields (MVP dimensions only).
- Aggregate Story overall_status up to Feature overall_status.
- Aggregate Feature overall_status up to Epic overall_status.

Rules
=====

Story overall_status (MVP):

Let dims = {
  testing_status,
  halo_adherence,
  guardrail_adherence,
  code_quality_adherence,
  security_policy_adherence
}

Normalise each dim:
  - pass / ok / success / compliant     -> Complete
  - fail / error / non_compliant        -> In Progress
  - not_run / planned / empty / missing -> Planned

Then:
  - Complete  if all dims Complete
  - Planned   if all dims Planned
  - In Progress otherwise

Feature overall_status:
  - Planned   if all child Stories Planned
  - Complete  if all child Stories Complete
  - In Progress otherwise

Epic overall_status:
  - Planned   if all child Features Planned
  - Complete  if all child Features Complete
  - In Progress otherwise

IMPORTANT:
- We ONLY ever write 'overall_status' + 'last_updated' fields.
- We NEVER touch the individual Story dimensions directly.
- We NEVER change the Story→Feature or Feature→Epic mapping;
  we only *read*:
    - Story.frontmatter.feature
    - Feature.frontmatter.epic
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"


# -------------------- basic helpers -------------------- #


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


def _replace_scalar(text: str, key: str, value: str) -> str:
    """
    Replace or insert 'key: value' in the front matter.
    We always insert before 'last_updated' if present, otherwise append.
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


def _now_iso_utc() -> str:
    """
    Current time in ISO UTC, matching the status model docs, e.g.
    2025-01-01T12:00:00Z
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _touch_last_updated(text: str) -> str:
    """
    Ensure last_updated is set to "now" in ISO UTC.
    """
    return _replace_scalar(text, "last_updated", _now_iso_utc())


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


def _norm_dim(raw: Optional[str]) -> str:
    """
    Normalise a Story dimension value into one of:
        Planned | In Progress | Complete

    Used for:
      testing_status
      halo_adherence
      guardrail_adherence
      code_quality_adherence
      security_policy_adherence
    """
    if raw is None:
        return "Planned"

    t = raw.strip().strip("\"'")
    tl = t.lower()

    if tl in {"pass", "ok", "success", "successful", "compliant"}:
        return "Complete"

    if tl in {"fail", "failed", "error", "errors", "non_compliant", "non-compliant"}:
        return "In Progress"

    # Treat not_run, planned, empty, and unknown as Planned (no evidence yet)
    if tl in {"not_run", "not-run", "pending", "planned", ""}:
        return "Planned"

    # Default safely to "In Progress" if it's something unexpected but non-empty
    return "In Progress"


def _derive_story_overall(text: str) -> str:
    """
    Derive Story overall_status from the 5 MVP dimensions.
    """
    dims_keys = [
        "testing_status",
        "halo_adherence",
        "guardrail_adherence",
        "code_quality_adherence",
        "security_policy_adherence",
    ]

    dim_states: List[str] = []
    for key in dims_keys:
        raw = _extract_scalar(text, key)
        dim_states.append(_norm_dim(raw))

    # Aggregate those Planned/In Progress/Complete values
    agg = _aggregate_overall(dim_states)
    if agg is None:
        # shouldn't happen (we always have 5 dims) but be defensive
        return "Planned"
    return agg


# -------------------- roll-up implementation -------------------- #


def rollup_stories() -> Dict[str, Dict[str, str]]:
    """
    Process Stories:

    - Derive Story overall_status from dimension fields.
    - Update overall_status + last_updated when it changes.
    - Build mapping Story -> Feature and Story overall_status.

    Returns:
        {
          "story_status": {story_id: overall_status},
          "story_feature": {story_id: feature_id},
        }
    """
    story_status: Dict[str, str] = {}
    story_feature: Dict[str, str] = {}

    print(">>> Rolling up Story statuses...")
    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)
        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue

        feature_id = _extract_scalar(text, "feature")
        if not feature_id:
            # If a Story is not mapped to a Feature, we skip it for roll-up
            print(f"    [WARN] Story {story_id} has no 'feature' mapping; skipping.")
            continue

        old_overall_raw = _extract_scalar(text, "overall_status")
        old_overall = _norm_overall(old_overall_raw)
        new_overall = _derive_story_overall(text)

        if new_overall != old_overall:
            new_text = _replace_scalar(text, "overall_status", new_overall)
            new_text = _touch_last_updated(new_text)
            _write(path, new_text)
            print(f"    Story {story_id}: {old_overall} -> {new_overall}")
        else:
            # still ensure we store the normalised value
            new_overall = old_overall

        story_status[story_id] = new_overall
        story_feature[story_id] = feature_id

    return {
        "story_status": story_status,
        "story_feature": story_feature,
    }


def rollup_features(story_status: Dict[str, str], story_feature: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Process Features:

    - Determine child Stories from the Story->Feature mapping.
    - Aggregate their overall_status to Feature overall_status.
    - Update Feature overall_status + last_updated when it changes.
    - Build mapping Feature -> Epic and Feature overall_status.

    Returns:
        {
          "feature_status": {feature_id: overall_status},
          "feature_epic": {feature_id: epic_id},
        }
    """
    # Build feature -> [story_id] from story_feature mapping
    stories_by_feature: Dict[str, List[str]] = {}
    for sid, fid in story_feature.items():
        stories_by_feature.setdefault(fid, []).append(sid)

    feature_status: Dict[str, str] = {}
    feature_epic: Dict[str, str] = {}

    print(">>> Rolling up Feature statuses...")
    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)
        feature_id = _extract_scalar(text, "feature_id")
        if not feature_id:
            continue

        epic_id = _extract_scalar(text, "epic")
        if epic_id:
            feature_epic[feature_id] = epic_id

        child_story_ids = stories_by_feature.get(feature_id, [])
        child_overalls = [story_status[sid] for sid in child_story_ids if sid in story_status]

        agg = _aggregate_overall(child_overalls)
        if agg is None:
            # No child stories mapped; leave overall_status as-is
            old = _norm_overall(_extract_scalar(text, "overall_status"))
            feature_status[feature_id] = old
            if not child_story_ids:
                print(f"    [WARN] Feature {feature_id} has no mapped Stories; leaving status as {old}.")
            else:
                print(f"    [WARN] Feature {feature_id} has Stories but none with known status; leaving as {old}.")
            continue

        old_overall = _norm_overall(_extract_scalar(text, "overall_status"))
        new_overall = agg

        if new_overall != old_overall:
            new_text = _replace_scalar(text, "overall_status", new_overall)
            new_text = _touch_last_updated(new_text)
            _write(path, new_text)
            print(f"    Feature {feature_id}: {old_overall} -> {new_overall}")
        else:
            new_overall = old_overall

        feature_status[feature_id] = new_overall

    return {
        "feature_status": feature_status,
        "feature_epic": feature_epic,
    }


def rollup_epics(feature_status: Dict[str, str], feature_epic: Dict[str, str]) -> None:
    """
    Process Epics:

    - Determine child Features from the Feature->Epic mapping.
    - Aggregate their overall_status to Epic overall_status.
    - Update Epic overall_status + last_updated when it changes.
    """
    # Build epic -> [feature_id] from feature_epic mapping
    features_by_epic: Dict[str, List[str]] = {}
    for fid, eid in feature_epic.items():
        features_by_epic.setdefault(eid, []).append(fid)

    print(">>> Rolling up Epic statuses...")
    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)
        epic_id = _extract_scalar(text, "epic_id")
        if not epic_id:
            continue

        child_feature_ids = features_by_epic.get(epic_id, [])
        child_overalls = [feature_status[fid] for fid in child_feature_ids if fid in feature_status]

        agg = _aggregate_overall(child_overalls)
        if agg is None:
            old = _norm_overall(_extract_scalar(text, "overall_status"))
            if not child_feature_ids:
                print(f"    [WARN] Epic {epic_id} has no mapped Features; leaving status as {old}.")
            else:
                print(f"    [WARN] Epic {epic_id} has Features but none with known status; leaving as {old}.")
            continue

        old_overall = _norm_overall(_extract_scalar(text, "overall_status"))
        new_overall = agg

        if new_overall != old_overall:
            new_text = _replace_scalar(text, "overall_status", new_overall)
            new_text = _touch_last_updated(new_text)
            _write(path, new_text)
            print(f"    Epic {epic_id}: {old_overall} -> {new_overall}")


# -------------------- CLI -------------------- #


def main() -> int:
    print("=== Mission Control Overall Status Roll-up ===")
    print(f"Repo root: {REPO_ROOT}")

    story_maps = rollup_stories()
    feature_maps = rollup_features(
        story_status=story_maps["story_status"],
        story_feature=story_maps["story_feature"],
    )
    rollup_epics(
        feature_status=feature_maps["feature_status"],
        feature_epic=feature_maps["feature_epic"],
    )

    print("=== Roll-up complete. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
