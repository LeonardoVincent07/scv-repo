#!/usr/bin/env python
"""
Mission Control Status Snapshot

Generates a human-readable markdown snapshot of the current status for:
- Epics
- Features
- Stories

Input (read-only):
  docs/mission_destination/epics/*.md
  docs/mission_destination/features/*.md
  docs/mission_destination/stories/*.md

Output:
  missionlog/status/status_snapshot.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"

SNAPSHOT_DIR = REPO_ROOT / "missionlog" / "status"
SNAPSHOT_PATH = SNAPSHOT_DIR / "status_snapshot.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    Extract a simple YAML list:

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


def _safe_status(val: Optional[str]) -> str:
    """
    Normalise status-ish values into something readable.
    We assume rollup_statuses.py has already normalised to:
      Planned | In Progress | Complete
    but we guard anyway.
    """
    if not val:
        return ""
    t = val.strip().strip('"\'')
    # Light normalisation
    lookup = {
        "planned": "Planned",
        "in progress": "In Progress",
        "in_progress": "In Progress",
        "in-progress": "In Progress",
        "complete": "Complete",
        "completed": "Complete",
        "done": "Complete",
    }
    return lookup.get(t.lower(), t)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EpicRow:
    epic_id: str
    name: str
    overall: str
    testing: str
    guardrail: str
    code_quality: str
    security: str


@dataclass
class FeatureRow:
    feature_id: str
    epic_id: str
    name: str
    overall: str
    testing: str
    guardrail: str
    code_quality: str
    security: str
    stories: List[str]


@dataclass
class StoryRow:
    story_id: str
    feature_id: str
    name: str
    overall: str
    testing: str
    guardrail: str
    code_quality: str
    security: str


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------

def collect_epics() -> Dict[str, EpicRow]:
    rows: Dict[str, EpicRow] = {}

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)

        epic_id = _extract_scalar(text, "epic_id")
        if not epic_id:
            continue  # legacy / out-of-scope epic

        name = _extract_scalar(text, "name") or path.stem

        overall = _safe_status(_extract_scalar(text, "overall_status"))
        testing = _safe_status(_extract_scalar(text, "testing_status"))
        guardrail = _safe_status(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _safe_status(_extract_scalar(text, "code_quality_adherence"))
        security = _safe_status(_extract_scalar(text, "security_policy_adherence"))

        rows[epic_id] = EpicRow(
            epic_id=epic_id,
            name=name,
            overall=overall,
            testing=testing,
            guardrail=guardrail,
            code_quality=code_quality,
            security=security,
        )

    return rows


def collect_features() -> Dict[str, FeatureRow]:
    rows: Dict[str, FeatureRow] = {}

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)

        feature_id = _extract_scalar(text, "feature_id")
        if not feature_id:
            continue  # legacy / out-of-scope feature

        epic_id = _extract_scalar(text, "epic") or ""
        name = _extract_scalar(text, "name") or path.stem

        stories = _extract_yaml_list(text, "stories")

        overall = _safe_status(_extract_scalar(text, "overall_status"))
        testing = _safe_status(_extract_scalar(text, "testing_status"))
        guardrail = _safe_status(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _safe_status(_extract_scalar(text, "code_quality_adherence"))
        security = _safe_status(_extract_scalar(text, "security_policy_adherence"))

        rows[feature_id] = FeatureRow(
            feature_id=feature_id,
            epic_id=epic_id,
            name=name,
            overall=overall,
            testing=testing,
            guardrail=guardrail,
            code_quality=code_quality,
            security=security,
            stories=stories,
        )

    return rows


def collect_stories() -> Dict[str, StoryRow]:
    rows: Dict[str, StoryRow] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue  # legacy / out-of-scope story

        feature_id = _extract_scalar(text, "feature") or ""
        name = _extract_scalar(text, "name") or path.stem

        overall = _safe_status(_extract_scalar(text, "overall_status"))
        testing = _safe_status(_extract_scalar(text, "testing_status"))
        guardrail = _safe_status(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _safe_status(_extract_scalar(text, "code_quality_adherence"))
        security = _safe_status(_extract_scalar(text, "security_policy_adherence"))

        rows[story_id] = StoryRow(
            story_id=story_id,
            feature_id=feature_id,
            name=name,
            overall=overall,
            testing=testing,
            guardrail=guardrail,
            code_quality=code_quality,
            security=security,
        )

    return rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _render_epics_table(epics: Dict[str, EpicRow]) -> str:
    if not epics:
        return "_No epics found._\n"

    lines: List[str] = []
    lines.append("| Epic | Name | Overall | Testing | Guardrails | Code Quality | Security |")
    lines.append("|------|------|---------|---------|-----------|--------------|----------|")

    for epic_id in sorted(epics.keys()):
        e = epics[epic_id]
        lines.append(
            f"| {e.epic_id} | {e.name} | {e.overall} | {e.testing} | "
            f"{e.guardrail} | {e.code_quality} | {e.security} |"
        )

    return "\n".join(lines) + "\n"


def _render_features_table(features: Dict[str, FeatureRow]) -> str:
    if not features:
        return "_No features found._\n"

    lines: List[str] = []
    lines.append("| Feature | Epic | Name | Overall | Testing | Guardrails | Code Quality | Security | Stories |")
    lines.append("|---------|------|------|---------|---------|-----------|--------------|----------|---------|")

    for fid in sorted(features.keys()):
        f = features[fid]
        stories_str = ", ".join(f.stories) if f.stories else ""
        lines.append(
            f"| {f.feature_id} | {f.epic_id} | {f.name} | {f.overall} | {f.testing} | "
            f"{f.guardrail} | {f.code_quality} | {f.security} | {stories_str} |"
        )

    return "\n".join(lines) + "\n"


def _render_stories_table(stories: Dict[str, StoryRow]) -> str:
    if not stories:
        return "_No stories found._\n"

    lines: List[str] = []
    lines.append("| Story | Feature | Name | Overall | Testing | Guardrails | Code Quality | Security |")
    lines.append("|-------|---------|------|---------|---------|-----------|--------------|----------|")

    for sid in sorted(stories.keys()):
        s = stories[sid]
        lines.append(
            f"| {s.story_id} | {s.feature_id} | {s.name} | {s.overall} | {s.testing} | "
            f"{s.guardrail} | {s.code_quality} | {s.security} |"
        )

    return "\n".join(lines) + "\n"


def build_snapshot_markdown() -> str:
    epics = collect_epics()
    features = collect_features()
    stories = collect_stories()

    parts: List[str] = []
    parts.append("# Mission Control Status Snapshot\n")

    parts.append("## Epics\n")
    parts.append(_render_epics_table(epics))

    parts.append("\n## Features\n")
    parts.append(_render_features_table(features))

    parts.append("\n## Stories\n")
    parts.append(_render_stories_table(stories))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Generating Mission Control Status Snapshot ===")
    print(f"Repo root: {REPO_ROOT}")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    markdown = build_snapshot_markdown()
    SNAPSHOT_PATH.write_text(markdown, encoding="utf-8")

    print(f"Wrote snapshot to {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
