#!/usr/bin/env python
"""
Mission Control Status Snapshot

Reads epics, features, and stories and writes:

  missionlog/status/status_snapshot.md     (Markdown tables for humans)
  app_frontend/public/missionlog/status_snapshot.json  (JSON for MissionLog UI)

Markdown contains three tables:
- Epics:    Epic | Name | Overall
- Features: Feature | Epic | Name | Overall | Stories
- Stories:  Story | Feature | Name | Overall

JSON contains a nested structure:

{
  "generated_at": "...",
  "epics": [
    {
      "epic_id": "...",
      "name": "...",
      "overall_status": "...",
      "features": [
        {
          "feature_id": "...",
          "name": "...",
          "epic_id": "...",
          "overall_status": "...",
          "stories": [
            {
              "story_id": "...",
              "name": "...",
              "feature_id": "...",
              "overall_status": "...",
              "testing_status": "...",
              "halo_adherence": "...",
              "guardrail_adherence": "...",
              "code_quality_adherence": "...",
              "security_policy_adherence": "..."
            }
          ]
        }
      ]
    }
  ]
}
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

EPICS_DIR = REPO_ROOT / "docs" / "mission_destination" / "epics"
FEATURES_DIR = REPO_ROOT / "docs" / "mission_destination" / "features"
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"

SNAPSHOT_DIR = REPO_ROOT / "missionlog" / "status"
SNAPSHOT_PATH = SNAPSHOT_DIR / "status_snapshot.md"

PUBLIC_STATUS_DIR = REPO_ROOT / "app_frontend" / "public" / "missionlog"
PUBLIC_STATUS_JSON = PUBLIC_STATUS_DIR / "status_snapshot.json"


# -------------------- helpers -------------------- #

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_scalar(text: str, key: str) -> Optional[str]:
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, flags=re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val and val[0] in {"'", '"'} and val[-1:] == val[0]:
        val = val[1:-1]
    return val or None


def _extract_yaml_list(text: str, key: str) -> List[str]:
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


def _safe_overall(val: Optional[str]) -> str:
    if not val:
        return ""
    t = val.strip().strip('"\'')
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


def _safe_dim(val: Optional[str]) -> str:
    """
    Normalise dimension statuses to: pass / fail / not_run.
    """
    if not val:
        return "not_run"
    t = val.strip().strip('"\'').lower()
    if t in {"pass", "ok", "success", "compliant"}:
        return "pass"
    if t in {"fail", "error", "non_compliant", "non-compliant"}:
        return "fail"
    if t in {"not_run", "not run", "pending", "planned"}:
        return "not_run"
    return t


# -------------------- data structures -------------------- #

@dataclass
class EpicRow:
    epic_id: str
    name: str
    overall: str


@dataclass
class FeatureRow:
    feature_id: str
    epic_id: str
    name: str
    overall: str
    stories: List[str]


@dataclass
class StoryRow:
    story_id: str
    feature_id: str
    name: str
    overall: str
    testing_status: str
    halo_adherence: str
    guardrail_adherence: str
    code_quality_adherence: str
    security_policy_adherence: str


# -------------------- collectors -------------------- #

def collect_epics() -> Dict[str, EpicRow]:
    rows: Dict[str, EpicRow] = {}

    for path in sorted(EPICS_DIR.glob("*.md")):
        text = _read(path)

        epic_id = _extract_scalar(text, "epic_id")
        if not epic_id:
            continue

        name = _extract_scalar(text, "name") or path.stem
        overall = _safe_overall(_extract_scalar(text, "overall_status"))

        rows[epic_id] = EpicRow(
            epic_id=epic_id,
            name=name,
            overall=overall,
        )

    return rows


def collect_features() -> Dict[str, FeatureRow]:
    rows: Dict[str, FeatureRow] = {}

    for path in sorted(FEATURES_DIR.glob("*.md")):
        text = _read(path)

        feature_id = _extract_scalar(text, "feature_id")
        if not feature_id:
            continue

        epic_id = _extract_scalar(text, "epic") or ""
        name = _extract_scalar(text, "name") or path.stem
        overall = _safe_overall(_extract_scalar(text, "overall_status"))
        stories = _extract_yaml_list(text, "stories")

        rows[feature_id] = FeatureRow(
            feature_id=feature_id,
            epic_id=epic_id,
            name=name,
            overall=overall,
            stories=stories,
        )

    return rows


def collect_stories() -> Dict[str, StoryRow]:
    rows: Dict[str, StoryRow] = {}

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = _read(path)

        story_id = _extract_scalar(text, "story_id")
        if not story_id:
            continue

        feature_id = _extract_scalar(text, "feature")
        name = _extract_scalar(text, "name") or path.stem
        overall = _safe_overall(_extract_scalar(text, "overall_status"))

        testing = _safe_dim(_extract_scalar(text, "testing_status"))
        halo = _safe_dim(_extract_scalar(text, "halo_adherence"))
        guardrail = _safe_dim(_extract_scalar(text, "guardrail_adherence"))
        code_quality = _safe_dim(_extract_scalar(text, "code_quality_adherence"))
        security = _safe_dim(_extract_scalar(text, "security_policy_adherence"))

        rows[story_id] = StoryRow(
            story_id=story_id,
            feature_id=feature_id or "",
            name=name,
            overall=overall,
            testing_status=testing,
            halo_adherence=halo,
            guardrail_adherence=guardrail,
            code_quality_adherence=code_quality,
            security_policy_adherence=security,
        )

    return rows


# -------------------- Markdown renderers -------------------- #

def _render_epics_table(epics: Dict[str, EpicRow]) -> str:
    if not epics:
        return "_No epics found._\n"

    lines: List[str] = []
    lines.append("| Epic | Name | Overall |")
    lines.append("|------|------|---------|")

    for eid in sorted(epics.keys()):
        e = epics[eid]
        lines.append(f"| {e.epic_id} | {e.name} | {e.overall} |")

    return "\n".join(lines) + "\n"


def _render_features_table(features: Dict[str, FeatureRow],
                           feature_to_story_ids: Dict[str, List[str]]) -> str:
    if not features:
        return "_No features found._\n"

    lines: List[str] = []
    lines.append("| Feature | Epic | Name | Overall | Stories |")
    lines.append("|---------|------|------|---------|---------|")

    for fid in sorted(features.keys()):
        f = features[fid]
        story_ids = feature_to_story_ids.get(fid, f.stories or [])
        stories_str = ", ".join(sorted(story_ids)) if story_ids else ""
        lines.append(
            f"| {f.feature_id} | {f.epic_id} | {f.name} | {f.overall} | {stories_str} |"
        )

    return "\n".join(lines) + "\n"


def _render_stories_table(stories: Dict[str, StoryRow]) -> str:
    if not stories:
        return "_No stories found._\n"

    lines: List[str] = []
    lines.append("| Story | Feature | Name | Overall |")
    lines.append("|-------|---------|------|---------|")

    for sid in sorted(stories.keys()):
        s = stories[sid]
        lines.append(f"| {s.story_id} | {s.feature_id} | {s.name} | {s.overall} |")

    return "\n".join(lines) + "\n"


def build_snapshot_markdown() -> str:
    epics = collect_epics()
    features = collect_features()
    stories = collect_stories()

    # Golden mapping: story.feature_id drives which stories belong to a feature.
    feature_to_story_ids: Dict[str, List[str]] = {}
    for s in stories.values():
        if not s.feature_id:
            continue
        feature_to_story_ids.setdefault(s.feature_id, []).append(s.story_id)

    parts: List[str] = []
    parts.append("# Mission Control Status Snapshot\n")

    parts.append("## Epics\n")
    parts.append(_render_epics_table(epics))

    parts.append("\n## Features\n")
    parts.append(_render_features_table(features, feature_to_story_ids))

    parts.append("\n## Stories\n")
    parts.append(_render_stories_table(stories))

    return "\n".join(parts)


# -------------------- JSON snapshot for MissionLog -------------------- #

def build_snapshot_json() -> Dict[str, object]:
    epics = collect_epics()
    features = collect_features()
    stories = collect_stories()

    # Map feature -> [StoryRow] via golden mapping (Story.feature_id)
    feature_to_stories: Dict[str, List[StoryRow]] = {}
    for s in stories.values():
        if not s.feature_id:
            continue
        feature_to_stories.setdefault(s.feature_id, []).append(s)

    # Map epic -> [FeatureRow] via Feature.epic_id
    epic_to_features: Dict[str, List[FeatureRow]] = {}
    for f in features.values():
        if not f.epic_id:
            continue
        epic_to_features.setdefault(f.epic_id, []).append(f)

    epics_payload: List[Dict[str, object]] = []

    for eid in sorted(epics.keys()):
        e = epics[eid]
        feature_rows = sorted(
            epic_to_features.get(eid, []),
            key=lambda fr: fr.feature_id,
        )

        features_payload: List[Dict[str, object]] = []
        for f in feature_rows:
            story_rows = sorted(
                feature_to_stories.get(f.feature_id, []),
                key=lambda sr: sr.story_id,
            )
            stories_payload: List[Dict[str, object]] = []
            for s in story_rows:
                stories_payload.append(
                    {
                        "story_id": s.story_id,
                        "name": s.name,
                        "feature_id": s.feature_id,
                        "overall_status": s.overall,
                        "testing_status": s.testing_status,
                        "halo_adherence": s.halo_adherence,
                        "guardrail_adherence": s.guardrail_adherence,
                        "code_quality_adherence": s.code_quality_adherence,
                        "security_policy_adherence": s.security_policy_adherence,
                    }
                )

            features_payload.append(
                {
                    "feature_id": f.feature_id,
                    "name": f.name,
                    "epic_id": f.epic_id,
                    "overall_status": f.overall,
                    "stories": stories_payload,
                }
            )

        epics_payload.append(
            {
                "epic_id": e.epic_id,
                "name": e.name,
                "overall_status": e.overall,
                "features": features_payload,
            }
        )

    return {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "epics": epics_payload,
    }


# -------------------- CLI -------------------- #

def main() -> int:
    print("=== Generating Mission Control Status Snapshot (overall + JSON) ===")
    print(f"Repo root: {REPO_ROOT}")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_STATUS_DIR.mkdir(parents=True, exist_ok=True)

    # Markdown snapshot (for the repo / docs)
    markdown = build_snapshot_markdown()
    SNAPSHOT_PATH.write_text(markdown, encoding="utf-8")
    print(f"Wrote Markdown snapshot to {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")

    # JSON snapshot (for MissionLog UI)
    json_data = build_snapshot_json()
    PUBLIC_STATUS_JSON.write_text(
        json.dumps(json_data, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote JSON snapshot to {PUBLIC_STATUS_JSON.relative_to(REPO_ROOT)}")

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
