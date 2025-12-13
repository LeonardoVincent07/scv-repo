from sqlalchemy import text
from database import SessionLocal

def test_db_connection():
    db = SessionLocal()
    try:
        value = db.execute(text("SELECT 1")).scalar_one()
        print(f"Database connected successfully! SELECT 1 returned: {value}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db_connection()



