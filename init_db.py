"""
Script to initialize the database with an admin user
Run this script once to create the admin user in the database
"""
from database import SessionLocal, engine, Base
from dao import UserDAO

# Create tables
Base.metadata.create_all(bind=engine)

def init_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = UserDAO.get_by_username(db, "admin")
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user with password "admin123" using DAO
        admin_user = UserDAO.create_user(
            db=db,
            username="admin",
            email="admin@example.com",
            password="admin123",
            roles=["ROLE_ADMIN", "ROLE_USER"]
        )

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
