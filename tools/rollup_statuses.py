#!/usr/bin/env python
"""
Mission Control Status Roll-up (clean version)

- DOES NOT create story_statuses or feature_statuses.
- ONLY updates these fields on Features and Epics:

  overall_status
  testing_status
  guardrail_adherence
  code_quality_adherence
  security_policy_adherence

Roll-up rules (same for each dimension):

- Planned    if all children are Planned
- Complete   if all children are Complete
- In Progress otherwise

Story values are messy; we normalise them on the fly.

Directory layout (as used today):

  docs/mission_destination/stories/*.md
  docs/mission_destination/features/*.md
  docs/mission_destination/epics/*.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"

# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

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

    # Fallback: append at end of front matter
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def _extract_yaml_list(text: str, key: str) -> List[str]:
    """
    Extract:

      key:
        - item1
        - item2

    Returns [item1, item2]
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
# Normalisation logic
# ---------------------------------------------------------------------------

def _norm_overall(raw_overall: Optional[str], raw_status: Optional[str]) -> str:
    """
    Normalise Story overall status to:

        Planned | In Progress | Complete
    """
    def norm_token(token: str) -> Optional[str]:
        t = token.strip().strip('"\'').lower()
        if t in {"planned"}:
            return "Planned"
        if t in {"in_progress", "in-progress", "in progress", "active"}:
            return "In Progress"
        if t in {"complete", "completed", "done"}:
            return "Complete"
        return None

    if raw_overall:
        v = norm_token(raw_overall)
        if v:
            return v

    if raw_status:
        v = norm_token(raw_status)
        if v:
            return v

    # Default if unknown
    return "Planned"


def _norm_dim_value(raw: Optional[str]) -> str:
    """
    Normalise messy Story dimension values (testing_status, guardrail_adherence,
    code_quality_adherence, security_policy_adherence) into:

        Planned | In Progress | Complete

    Heuristics:
    - If already one of those (case-insensitive), keep it.
    - Pass-like -> Complete
    - Fail-like -> In Progress
    - Not-run / unknown / empty -> Planned
    """
    if raw is None:
        return "Planned"

    t = raw.strip().strip('"\'')
    tl = t.lower()

    # Already canonical?
    if tl in {"planned"}:
        return "Planned"
    if tl in {"in progress", "in_progress", "in-progress"}:
        return "In Progress"
    if tl in {"complete", "completed"}:
        return "Complete"

    # Pass-ish
    if tl in {"pass", "passed", "ok", "success", "succeeded", "compliant", "true", "yes"}:
        return "Complete"

    # Fail-ish
    if tl in {"fail", "failed", "error", "non_compliant", "non-compliant", "false", "no"}:
        return "In Progress"

    # Not-run-ish
    if tl in {"not_run", "not-run", "not run", "pending", "todo", "tbd", "unknown", "n/a", "na", ""}:
        return "Planned"

    # Default – we've at least touched it
    return "In Progress"


def _aggregate(child_statuses: List[str]) -> Optional[str]:
    """
    Roll-up:

    - Planned   if all children Planned
    - Complete  if all children Complete
    - In Progress otherwise

    Returns None if there are no children (caller decides what to do).
    """
    if not child_statuses:
        return None
    s = set(child_statuses)
    if s == {"Planned"}:
        return "Planned"
    if s == {"Complete"}:
        return "Complete"
    return "In Progress"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class StoryStatus:
    story_id: str
    feature_id: Optional[str]
    overall: str
    testing: str
    guardrail: str
    code_quality: str
    security: str


@dataclass
class FeatureStatus:
    feature_id: str
    epic_id: Optional[str]
    stories: List[str]
    overall: str
    testing: str
    guardrail: str
    code_quality: str
    security: str


# ---------------------------------------------------------------------------
# Collect Story-level status
# ---------------------------------------------------------------------------

def collect_stories() -> Dict[str, StoryStatus]:
    stories: Dict[str, StoryStatus] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        sid = _extract_scalar(text, "story_id")
        if not sid:
            continue  # non-Mission story, ignore

        feature_id = _extract_scalar(text, "feature")

        raw_overall = _extract_scalar(text, "overall_status")
        raw_status_fallback = _extract_scalar(text, "status")

        overall = _norm_overall(raw_overall, raw_status_fallback)

        testing = _norm_dim_value(_extract_scalar(text, "testing_status"))
        guardrail = _norm_dim_value(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _norm_dim_value(_extract_scalar(text, "code_quality_adherence"))
        security = _norm_dim_value(_extract_scalar(text, "security_policy_adherence"))

        stories[sid] = StoryStatus(
            story_id=sid,
            feature_id=feature_id,
            overall=overall,
            testing=testing,
            guardrail=guardrail,
            code_quality=code_quality,
            security=security,
        )

    return stories


# ---------------------------------------------------------------------------
# Roll up to Features
# ---------------------------------------------------------------------------

def rollup_features(stories: Dict[str, StoryStatus]) -> Dict[str, FeatureStatus]:
    feature_statuses: Dict[str, FeatureStatus] = {}

    # First pass: build a feature -> [story_ids] mapping from story.feature_id
    feature_to_stories: Dict[str, List[str]] = {}
    for s in stories.values():
        if not s.feature_id:
            continue
        feature_to_stories.setdefault(s.feature_id, []).append(s.story_id)

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)

        fid = _extract_scalar(text, "feature_id")
        if not fid:
            continue  # ignore non-Mission feature docs

        epic_id = _extract_scalar(text, "epic")

        # Prefer explicit list in front matter if present, otherwise derive
        listed_story_ids = _extract_yaml_list(text, "stories")
        if listed_story_ids:
            story_ids = listed_story_ids
        else:
            story_ids = feature_to_stories.get(fid, [])

        child_overall: List[str] = []
        child_testing: List[str] = []
        child_guardrail: List[str] = []
        child_code_quality: List[str] = []
        child_security: List[str] = []

        for sid in story_ids:
            s = stories.get(sid)
            if s is None:
                # Unknown story – treat as Planned on all dimensions
                child_overall.append("Planned")
                child_testing.append("Planned")
                child_guardrail.append("Planned")
                child_code_quality.append("Planned")
                child_security.append("Planned")
            else:
                child_overall.append(s.overall)
                child_testing.append(s.testing)
                child_guardrail.append(s.guardrail)
                child_code_quality.append(s.code_quality)
                child_security.append(s.security)

        agg_overall = _aggregate(child_overall)
        agg_testing = _aggregate(child_testing)
        agg_guardrail = _aggregate(child_guardrail)
        agg_code_quality = _aggregate(child_code_quality)
        agg_security = _aggregate(child_security)

        new_text = text

        if agg_overall:
            new_text = _replace_scalar(new_text, "overall_status", agg_overall)
        if agg_testing:
            new_text = _replace_scalar(new_text, "testing_status", agg_testing)
        if agg_guardrail:
            new_text = _replace_scalar(new_text, "guardrail_adherence", agg_guardrail)
        if agg_code_quality:
            new_text = _replace_scalar(new_text, "code_quality_adherence", agg_code_quality)
        if agg_security:
            new_text = _replace_scalar(new_text, "security_policy_adherence", agg_security)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Updated Feature {fid} ({path.relative_to(REPO_ROOT)})")

        # Read back final values (in case we didn't aggregate some dims)
        final_text = _read(path)

        feature_statuses[fid] = FeatureStatus(
            feature_id=fid,
            epic_id=epic_id,
            stories=story_ids,
            overall=_extract_scalar(final_text, "overall_status") or "Planned",
            testing=_extract_scalar(final_text, "testing_status") or "Planned",
            guardrail=_extract_scalar(final_text, "guardrail_adherence") or "Planned",
            code_quality=_extract_scalar(final_text, "code_quality_adherence") or "Planned",
            security=_extract_scalar(final_text, "security_policy_adherence") or "Planned",
        )

    return feature_statuses


# ---------------------------------------------------------------------------
# Roll up to Epics
# ---------------------------------------------------------------------------

def rollup_epics(features: Dict[str, FeatureStatus]) -> None:
    # Build epic -> [feature_ids]
    epic_to_features: Dict[str, List[str]] = {}
    for f in features.values():
        if not f.epic_id:
            continue
        epic_to_features.setdefault(f.epic_id, []).append(f.feature_id)

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)

        eid = _extract_scalar(text, "epic_id")
        if not eid:
            continue

        feature_ids = epic_to_features.get(eid, [])

        child_overall: List[str] = []
        child_testing: List[str] = []
        child_guardrail: List[str] = []
        child_code_quality: List[str] = []
        child_security: List[str] = []

        for fid in feature_ids:
            f = features.get(fid)
            if f is None:
                child_overall.append("Planned")
                child_testing.append("Planned")
                child_guardrail.append("Planned")
                child_code_quality.append("Planned")
                child_security.append("Planned")
            else:
                child_overall.append(f.overall)
                child_testing.append(f.testing)
                child_guardrail.append(f.guardrail)
                child_code_quality.append(f.code_quality)
                child_security.append(f.security)

        agg_overall = _aggregate(child_overall)
        agg_testing = _aggregate(child_testing)
        agg_guardrail = _aggregate(child_guardrail)
        agg_code_quality = _aggregate(child_code_quality)
        agg_security = _aggregate(child_security)

        new_text = text

        if agg_overall:
            new_text = _replace_scalar(new_text, "overall_status", agg_overall)
        if agg_testing:
            new_text = _replace_scalar(new_text, "testing_status", agg_testing)
        if agg_guardrail:
            new_text = _replace_scalar(new_text, "guardrail_adherence", agg_guardrail)
        if agg_code_quality:
            new_text = _replace_scalar(new_text, "code_quality_adherence", agg_code_quality)
        if agg_security:
            new_text = _replace_scalar(new_text, "security_policy_adherence", agg_security)

        if new_text != text:
            _write(path, new_text)
            print(f">>> Updated Epic {eid} ({path.relative_to(REPO_ROOT)})")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Mission Control Status Roll-up (clean) ===")
    print(f"Repo root: {REPO_ROOT}")

    stories = collect_stories()
    print(f"Collected {len(stories)} Story statuses.")

    features = rollup_features(stories)
    print(f"Rolled up {len(features)} Features.")

    rollup_epics(features)
    print("Rolled up Epics.")

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

