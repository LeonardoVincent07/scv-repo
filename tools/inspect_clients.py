import sys
from pathlib import Path

# Ensure repo root is on the Python path (must be BEFORE importing database)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import text
from database import SessionLocal


def inspect_clients(limit: int = 5):
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT * FROM clients LIMIT :limit"),
            {"limit": limit},
        )
        rows = result.fetchall()

        print(f"\nSample rows from clients (limit {limit}):\n")
        for row in rows:
            print(dict(row._mapping))

    finally:
        db.close()


if __name__ == "__main__":
    inspect_clients()

