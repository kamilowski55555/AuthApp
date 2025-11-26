from db.database import engine, SessionLocal, Base, get_db, DB_PATH, BASE_DIR

# Resources directory for CSV files
import os
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
os.makedirs(DB_DIR, exist_ok=True)

__all__ = ["engine", "SessionLocal", "Base", "get_db", "DB_PATH", "BASE_DIR", "DB_DIR"]
