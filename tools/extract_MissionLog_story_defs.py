#!/usr/bin/env python3
"""
Export story markdown files into UI-consumable JSON for MissionLog.

Can be run from:
- repo root
- tools/ directory

Repo layout assumed:
  repo_root/
    docs/mission_destination/stories/
    app_frontend/public/missionlog/story_defs/
    tools/extract_MissionLog_story_defs.py
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


# -----------------------------
# Repo root detection
# -----------------------------

def detect_repo_root() -> Path:
  """
  Detect repo root as the parent of the 'tools' directory.
  This allows the script to be run from anywhere.
  """
  here = Path(__file__).resolve()
  if here.parent.name != "tools":
    raise RuntimeError(
      f"Expected script to live in a 'tools' directory, but found: {here}"
    )
  return here.parent.parent


REPO_ROOT = detect_repo_root()


# -----------------------------
# JSON safety helpers
# -----------------------------

def json_safe(value):
  """
  Recursively convert values to JSON-serialisable forms.
  - datetime/date -> ISO 8601 string
  """
  if isinstance(value, datetime):
    return value.replace(microsecond=0).isoformat()
  if isinstance(value, date):
    return value.isoformat()
  if isinstance(value, dict):
    return {k: json_safe(v) for k, v in value.items()}
  if isinstance(value, list):
    return [json_safe(v) for v in value]
  return value


# -----------------------------
# Data model
# -----------------------------

@dataclass(frozen=True)
class StoryDoc:
  story_id: str
  slug: str
  source_path: str
  front_matter: Dict[str, Any]
  body_markdown: str
  exported_at_utc: str


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


# -----------------------------
# Parsing helpers
# -----------------------------

def parse_story_markdown(md_text: str) -> Tuple[Dict[str, Any], str]:
  """
  Returns (front_matter_dict, body_markdown).
  If no front matter, returns ({}, full_text).
  """
  m = FRONT_MATTER_RE.match(md_text.strip() + "\n")
  if not m:
    return {}, md_text.strip()

  fm_raw = m.group(1)
  body = m.group(2).strip()

  front_matter = yaml.safe_load(fm_raw) or {}
  if not isinstance(front_matter, dict):
    raise ValueError("Front matter must be a YAML mapping/dict.")

  return front_matter, body


def infer_story_id(front_matter: Dict[str, Any], filename: str) -> str:
  for key in ("story_id", "id", "story"):
    if key in front_matter and front_matter[key]:
      return str(front_matter[key]).strip()

  m = re.match(r"^(ST-\d+)", filename, re.IGNORECASE)
  if m:
    return m.group(1).upper()

  raise ValueError(f"Could not infer story_id from front matter or filename: {filename}")


def slugify_filename(story_path: Path) -> str:
  return story_path.stem


def utc_now_iso() -> str:
  return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# -----------------------------
# Build + write
# -----------------------------

def build_story_doc(story_path: Path) -> StoryDoc:
  raw = story_path.read_text(encoding="utf-8")
  fm, body = parse_story_markdown(raw)
  story_id = infer_story_id(fm, story_path.name)

  return StoryDoc(
    story_id=story_id,
    slug=slugify_filename(story_path),
    source_path=str(story_path.relative_to(REPO_ROOT)).replace("\\", "/"),
    front_matter=fm,
    body_markdown=body,
    exported_at_utc=utc_now_iso(),
  )


def write_story_doc(out_dir: Path, doc: StoryDoc) -> Path:
  out_dir.mkdir(parents=True, exist_ok=True)
  out_path = out_dir / f"{doc.story_id}.json"

  payload = {
    "story_id": doc.story_id,
    "slug": doc.slug,
    "source_path": doc.source_path,
    "exported_at_utc": doc.exported_at_utc,
    "front_matter": json_safe(doc.front_matter),
    "body_markdown": doc.body_markdown,
  }

  out_path.write_text(
    json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
  )

  return out_path


# -----------------------------
# Main
# -----------------------------

def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--stories_dir",
    default="docs/mission_destination/stories",
    help="Directory containing story markdown files (relative to repo root).",
  )
  parser.add_argument(
    "--out_dir",
    default="app_frontend/public/missionlog/story_defs",
    help="Output directory for per-story JSON files (relative to repo root).",
  )
  args = parser.parse_args()

  stories_dir = (REPO_ROOT / args.stories_dir).resolve()
  out_dir = (REPO_ROOT / args.out_dir).resolve()

  if not stories_dir.exists():
    raise SystemExit(f"Stories dir not found: {stories_dir}")

  md_files = sorted(stories_dir.glob("ST-*.md"))
  if not md_files:
    print(f"No story files found under {stories_dir}")
    return 0

  written = 0
  for p in md_files:
    try:
      doc = build_story_doc(p)
      write_story_doc(out_dir, doc)
      written += 1
    except Exception as e:
      print(f"[ERROR] {p.name}: {e}")

  print(f"Exported {written} story definition file(s) to {out_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

