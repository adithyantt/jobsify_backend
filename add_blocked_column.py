from app.database import Base, engine
from sqlalchemy import text

# Add blocked column to users table
def add_blocked_column():
    try:
        with engine.connect() as conn:
            # Add the blocked column with default value False
            conn.execute(text("ALTER TABLE users ADD COLUMN blocked BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Successfully added 'blocked' column to users table")
    except Exception as e:
        print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_blocked_column()
