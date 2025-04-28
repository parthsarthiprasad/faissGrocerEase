from sqlalchemy import text
from app.db.database import engine, Base
import os

def reset_database():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Enable PostGIS extension if not already enabled
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

if __name__ == "__main__":
    reset_database()
    print("Database reset complete.") 