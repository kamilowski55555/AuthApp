from sqlalchemy.orm import Session
from model.user import User
from typing import Optional
import bcrypt


class UserDAO:
    """Data Access Object for User operations"""

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, roles: list) -> User:
        """Create a new user with hashed password"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password.decode('utf-8'),
            roles=roles
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password"""
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))



    @staticmethod
    def delete_user(db: Session, user: User) -> None:
        """Delete a user"""
        db.delete(user)
        db.commit()

