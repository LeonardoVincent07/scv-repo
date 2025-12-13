#!/usr/bin/env python
"""
Inspect the current database schema for the SCV backend.

- Imports the SQLAlchemy Base and engine from app_backend.db
- Ensures the repo root is on sys.path so `app_backend` can be imported
- Reflects all tables and prints their columns, types, PK/FK flags, etc.

Usage (from repo root):

    # Human-readable text (default)
    python tools/inspect_db_schema.py

    # Markdown tables (good for docs)
    python tools/inspect_db_schema.py markdown

This script is READ-ONLY with respect to data. It may create tables if they
don't exist yet via `Base.metadata.create_all(bind=engine)`, but it does not
insert, update, or delete any rows.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import inspect as sqla_inspect

# ---------------------------------------------------------------------------
# Repo root + sys.path so `app_backend` can be imported
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Now we can safely import the backend DB objects
from app_backend.db import Base, engine  # type: ignore[import]

# ---------------------------------------------------------------------------
# Core inspection helpers
# ---------------------------------------------------------------------------


def describe_schema() -> Dict[str, List[Dict[str, Any]]]:
    """
    Reflect the database schema via SQLAlchemy's Inspector.

    Returns:
        {
          "table_name": [
            {
              "name": "column_name",
              "type": "VARCHAR(255)",
              "nullable": False,
              "primary_key": True/False,
              "default": <default or None>,
              "fk": "other_table.other_column" or None,
            },
            ...
          ],
          ...
        }
    """
    # Ensure all models have been created (no-op if already present)
    Base.metadata.create_all(bind=engine)

    inspector = sqla_inspect(engine)
    schema: Dict[str, List[Dict[str, Any]]] = {}

    for table_name in inspector.get_table_names():
        pk_info = inspector.get_pk_constraint(table_name) or {}
        pk_cols = set(pk_info.get("constrained_columns") or [])

        fk_map: Dict[str, str] = {}
        for fk in inspector.get_foreign_keys(table_name):
            ref_table = fk.get("referred_table")
            ref_cols = fk.get("referred_columns") or []
            constrained_cols = fk.get("constrained_columns") or []
            for col_name, ref_col in zip(constrained_cols, ref_cols):
                fk_map[col_name] = f"{ref_table}.{ref_col}"

        col_infos: List[Dict[str, Any]] = []
        for col in inspector.get_columns(table_name):
            name = col["name"]
            col_infos.append(
                {
                    "name": name,
                    "type": str(col["type"]),
                    "nullable": bool(col.get("nullable", True)),
                    "primary_key": name in pk_cols,
                    "default": col.get("default"),
                    "fk": fk_map.get(name),
                }
            )

        schema[table_name] = col_infos

    return schema


def print_text(schema: Dict[str, List[Dict[str, Any]]]) -> None:
    """Pretty, human-readable text output."""
    if not schema:
        print("No tables found in the database.")
        return

    for table_name in sorted(schema.keys()):
        print(f"\n=== {table_name} ===")
        for col in schema[table_name]:
            flags: List[str] = []
            if col["primary_key"]:
                flags.append("PK")
            if col["fk"]:
                flags.append(f"FK -> {col['fk']}")
            if not col["nullable"]:
                flags.append("NOT NULL")

            flag_part = f" ({', '.join(flags)})" if flags else ""
            print(f"- {col['name']}: {col['type']}{flag_part}")


def print_markdown(schema: Dict[str, List[Dict[str, Any]]]) -> None:
    """Markdown table output (useful for docs/MissionAtlas)."""
    if not schema:
        print("No tables found in the database.")
        return

    for table_name in sorted(schema.keys()):
        print(f"\n### {table_name}\n")
        print("| Column | Type | Flags | Default |")
        print("|--------|------|-------|---------|")
        for col in schema[table_name]:
            flags: List[str] = []
            if col["primary_key"]:
                flags.append("PK")
            if col["fk"]:
                flags.append(f"FK -> {col['fk']}")
            if not col["nullable"]:
                flags.append("NOT NULL")

            flag_str = ", ".join(flags) if flags else ""
            default_str = str(col["default"]) if col["default"] is not None else ""
            print(f"| {col['name']} | {col['type']} | {flag_str} | {default_str} |")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: List[str]) -> int:
    fmt = (argv[0].lower() if argv else "text").strip()

    schema = describe_schema()
    if fmt == "markdown":
        print_markdown(schema)
    else:
        print_text(schema)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

