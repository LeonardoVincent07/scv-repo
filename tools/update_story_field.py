#!/usr/bin/env python
"""
Update a single front-matter field in a story markdown file.

Usage:
  python tools/update_story_field.py --story ST-05 --field halo_adherence --value pass
"""

import argparse
import sys
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Update a story front-matter field")
    parser.add_argument("--story", required=True, help="Story ID (e.g. ST-05)")
    parser.add_argument("--field", required=True, help="Front-matter field to update")
    parser.add_argument("--value", required=True, help="Value to set")
    return parser.parse_args()


def find_story_file(story_id: str) -> Path:
    stories_dir = Path("docs/mission_destination/stories")
    if not stories_dir.exists():
        raise FileNotFoundError(f"Stories directory not found: {stories_dir}")

    matches = list(stories_dir.glob(f"{story_id}_*.md"))
    if not matches:
        raise FileNotFoundError(f"No story file found for {story_id}")
    if len(matches) > 1:
        raise RuntimeError(f"Multiple story files found for {story_id}: {matches}")

    return matches[0]


def load_front_matter(text: str):
    if not text.startswith("---"):
        raise ValueError("Story file does not start with front matter ('---')")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Malformed front matter")

    front_matter = yaml.safe_load(parts[1]) or {}
    body = parts[2]

    return front_matter, body


def main():
    args = parse_args()

    story_file = find_story_file(args.story)

    raw = story_file.read_text(encoding="utf-8")
    front_matter, body = load_front_matter(raw)

    old_value = front_matter.get(args.field)
    front_matter[args.field] = args.value

    new_front = yaml.safe_dump(
        front_matter,
        sort_keys=False,
        default_flow_style=False,
    ).strip()

    updated = f"---\n{new_front}\n---{body}"

    story_file.write_text(updated, encoding="utf-8")

    print(
        f">>> Updated {story_file} -> "
        f"{args.field}: {old_value} -> {args.value}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
