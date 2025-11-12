"""
Script to initialize the database with an admin user
Run this script once to create the admin user in the database
"""
import bcrypt
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User

# Create tables
Base.metadata.create_all(bind=engine)

def init_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user with password "admin123"
        hashed_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt())

        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password.decode('utf-8'),
            roles=["ROLE_ADMIN", "ROLE_USER"]
        )

        db.add(admin_user)
        db.commit()
        print("✓ Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Roles: ROLE_ADMIN, ROLE_USER")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin_user()

