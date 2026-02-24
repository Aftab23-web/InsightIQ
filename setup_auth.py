"""
Setup script to initialize database with tables for authentication
Run this before using the application for the first time
"""
from database.models import init_db, Base, engine

def setup_database():
    """Initialize database and create all tables"""
    print("Initializing database...")
    try:
        init_db()
        print(" Database initialized successfully!")
        print(f" Tables created: {', '.join(Base.metadata.tables.keys())}")
        print("\n Authentication system is ready!")
        print("You can now run the application and register a new user.")
    except Exception as e:
        print(f" Error initializing database: {e}")

if __name__ == "__main__":
    setup_database()
