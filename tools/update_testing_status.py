import sys
from pathlib import Path
import re

def main():
    if len(sys.argv) != 3:
        print("Usage: update_testing_status.py <story_path> <status>")
        sys.exit(1)

    story_path = Path(sys.argv[1])
    status = sys.argv[2]

    if status not in {"not_run", "pass", "fail"}:
        print(f"Invalid status: {status}")
        sys.exit(1)

    text = story_path.read_text(encoding="utf-8")

    # Replace the first occurrence of 'testing_status: ...'
    pattern = r"(^testing_status:\s*).*$"
    replacement = rf"\1{status}"
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)

    if count == 0:
        print("No testing_status line found to update.")
        sys.exit(1)

    story_path.write_text(new_text, encoding="utf-8")

if __name__ == "__main__":
    main()
