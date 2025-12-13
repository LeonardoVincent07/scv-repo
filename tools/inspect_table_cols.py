import sys
from pathlib import Path

# Ensure repo root is on the Python path BEFORE imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import text
from database import SessionLocal


def show_columns(table_name: str):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :t
                ORDER BY ordinal_position
            """),
            {"t": table_name},
        ).fetchall()

        print(f"\nColumns for {table_name}:\n")
        for r in rows:
            print(f" - {r[0]} ({r[1]})")

    finally:
        db.close()


if __name__ == "__main__":
    for t in ["accounts", "client_operational_state", "match_decisions"]:
        show_columns(t)

