import sys
from pathlib import Path

# Ensure repo root is on the Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import text
from database import SessionLocal


def list_tables():
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
        )

        tables = [row[0] for row in result.fetchall()]

        print("\nTables in SCV database:\n")
        for t in tables:
            print(f" - {t}")

        print(f"\nTotal tables: {len(tables)}")

    finally:
        db.close()


if __name__ == "__main__":
    list_tables()

