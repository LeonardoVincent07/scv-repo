#!/usr/bin/env python
"""
Generate STORY_CONFIG snippets for a new Story.

This does NOT modify any files.
It just prints the blocks you should paste into:

- tools/run_story_tests.py
- tools/run_story_lint.py
- tools/run_story_security.py

Usage:

  python tools/generate_story_config_snippets.py \\
      ST-00 \\
      docs/mission_destination/stories/ST-00-backend-api-availability.md \\
      tests/api/http/test_st_00_backend_api_availability.py \\
      app_backend/main.py

You can pass multiple targets as comma-separated lists, e.g.:

  python tools/generate_story_config_snippets.py \\
      ST-99 \\
      docs/mission_destination/stories/ST-99_some_story.md \\
      tests/services/foo/test_st_99_foo.py,tests/api/http/test_st_99_foo_api.py \\
      src/services/foo/service.py,src/domain/models/foo.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _path_to_reproot_expr(rel_path: str) -> str:
    """
    Turn 'docs/mission_destination/stories/ST-03_map_identity_fields.md'
    into:

        REPO_ROOT
        / "docs"
        / "mission_destination"
        / "stories"
        / "ST-03_map_identity_fields.md"
    """
    parts = rel_path.replace("\\", "/").split("/")
    indent = " " * 8
    joined = ('"\n' + indent + '/ "').join(parts)
    return f"REPO_ROOT\n{indent}/ \"{joined}\""


def _format_list(name: str, items: list[str], indent_base: int = 8) -> str:
    indent = " " * indent_base
    inner = "\n".join(f'{indent}    "{item}",' for item in items)
    return f'{indent}"{name}": [\n{inner}\n{indent}],'


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print(
            "Usage:\n"
            "  python tools/generate_story_config_snippets.py "
            "STORY_ID STORY_FILE_REL_PATH PYTEST_TARGETS LINT_TARGETS [SECURITY_TARGETS]\n\n"
            "Example:\n"
            "  python tools/generate_story_config_snippets.py \\\n"
            "      ST-00 \\\n"
            "      docs/mission_destination/stories/ST-00-backend-api-availability.md \\\n"
            "      tests/api/http/test_st_00_backend_api_availability.py \\\n"
            "      app_backend/main.py\n"
        )
        return 1

    story_id = argv[1].upper()
    story_file_rel = argv[2]

    pytest_targets = [t.strip() for t in argv[3].split(",") if t.strip()]
    lint_targets = [t.strip() for t in argv[4].split(",") if t.strip()]

    if len(argv) >= 6:
        security_targets = [t.strip() for t in argv[5].split(",") if t.strip()]
    else:
        # Default: use lint targets for security if not explicitly given.
        security_targets = list(lint_targets)

    story_file_expr = _path_to_reproot_expr(story_file_rel)

    print("\n" + "=" * 72)
    print(f"STORY CONFIG SNIPPETS FOR {story_id}")
    print("=" * 72 + "\n")

    # ------------------------------------------------------------------
    # run_story_tests.py
    # ------------------------------------------------------------------
    print("# Paste into tools/run_story_tests.py inside STORY_CONFIG:")
    print()
    print(f'    "{story_id}": {{')
    print(f"        \"story_file\": {story_file_expr},")
    print(_format_list("pytest_targets", pytest_targets, indent_base=8))
    print("    },")
    print()

    # ------------------------------------------------------------------
    # run_story_lint.py
    # ------------------------------------------------------------------
    print("# Paste into tools/run_story_lint.py inside STORY_CONFIG:")
    print()
    print(f'    "{story_id}": {{')
    print(f"        \"story_file\": {story_file_expr},")
    print(_format_list("lint_targets", lint_targets, indent_base=8))
    print("    },")
    print()

    # ------------------------------------------------------------------
    # run_story_security.py
    # ------------------------------------------------------------------
    print("# Paste into tools/run_story_security.py inside STORY_CONFIG:")
    print()
    print(f'    "{story_id}": {{')
    print(f"        \"story_file\": {story_file_expr},")
    print(_format_list("security_targets", security_targets, indent_base=8))
    print("    },")
    print()

    # ------------------------------------------------------------------
    # Guardrails note
    # ------------------------------------------------------------------
    print("# NOTE: run_story_guardrails.py uses explicit _register_story(...) calls.")
    print("# If this Story should have guardrails, add a _register_story(...) block")
    print("# there manually, choosing an appropriate check function.")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
