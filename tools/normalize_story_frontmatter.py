#!/usr/bin/env python

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
STORIES_DIR = REPO_ROOT / "docs" / "mission_destination" / "stories"


def remove_implementation_presence(text: str) -> str:
    """
    Remove lines like:
      implementation_presence: false
    from the front matter.
    """
    return re.sub(
        r"^implementation_presence:\s*.*\n",
        "",
        text,
        flags=re.MULTILINE,
    )


def ensure_halo_pass(text: str) -> str:
    """
    Ensure there's a line:
      halo_adherence: pass

    - If halo_adherence already exists, set it to 'pass'.
    - If not, insert it before last_updated: if present,
      otherwise append near the end of the front matter.
    """
    pattern = r"^halo_adherence:\s*.*$"
    replacement = "halo_adherence: pass"

    # Case 1: replace existing line
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)

    # Case 2: insert before last_updated if present
    lu_pattern = r"^last_updated:\s*.*$"
    m = re.search(lu_pattern, text, flags=re.MULTILINE)
    if m:
        start = m.start()
        return text[:start] + replacement + "\n" + text[start:]

    # Case 3: append at end
    if not text.endswith("\n"):
        text += "\n"
    return text + replacement + "\n"


def main() -> int:
    print("=== Normalising story front matter ===")
    print(f"Stories dir: {STORIES_DIR}")

    updated = 0

    for path in sorted(STORIES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        new_text = remove_implementation_presence(text)
        new_text = ensure_halo_pass(new_text)

        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
            print(f"  updated {path.name}")

    print(f"Done. Updated {updated} story files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
