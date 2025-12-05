#!/usr/bin/env python

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"

def main() -> int:
    print("=== Removing implementation_presence from story front matter ===")
    count = 0

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        # Remove a line like: implementation_presence: false
        new_text = re.sub(
            r"^implementation_presence:\s*.*\n",
            "",
            text,
            flags=re.MULTILINE,
        )

        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            count += 1
            print(f"  cleaned {path.name}")

    print(f"Done. Updated {count} story files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
