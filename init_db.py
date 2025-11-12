"""
Script to initialize the database with an admin user
Run this script once to create the admin user in the database
"""
from database import SessionLocal, engine, Base
from dao import UserDAO


Base.metadata.create_all(bind=engine)

def init_admin_user():
    db = SessionLocal()
    try:

        existing_admin = UserDAO.get_by_username(db, "admin")
        if existing_admin:
            print("Admin user already exists!")
            return

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

def init_normal_user():
    db = SessionLocal()
    try:

        existing_admin = UserDAO.get_by_username(db, "user")
        if existing_admin:
            print("Admin user already exists!")
            return

        admin_user = UserDAO.create_user(
            db=db,
            username="user",
            email="user@example.com",
            password="user123",
            roles=["ROLE_USER"]
        )

        print("✓ Normal user created successfully!")
        print("  Username: user")
        print("  Password: user123")
        print("  Roles: ROLE_USER")

    except Exception as e:
        print(f"Error creating normal user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_admin_user()
    init_normal_user()
