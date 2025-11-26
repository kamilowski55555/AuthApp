from sqlalchemy.orm import Session
from model.rating import Rating
from typing import Optional, List
from sqlalchemy import func


class RatingDAO:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Rating]:
        """Get all ratings with pagination."""
        return db.query(Rating).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, rating_id: int) -> Optional[Rating]:
        """Get a rating by its ID."""
        return db.query(Rating).filter(Rating.id == rating_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Rating]:
        """Get all ratings by a specific user."""
        return db.query(Rating).filter(Rating.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_movie_id(db: Session, movie_id: int, skip: int = 0, limit: int = 100) -> List[Rating]:
        """Get all ratings for a specific movie."""
        return db.query(Rating).filter(Rating.movie_id == movie_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_user_and_movie(db: Session, user_id: int, movie_id: int) -> Optional[Rating]:
        """Get a specific user's rating for a specific movie."""
        return db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        ).first()

    @staticmethod
    def get_average_rating(db: Session, movie_id: int) -> Optional[float]:
        """Get the average rating for a movie."""
        result = db.query(func.avg(Rating.rating)).filter(Rating.movie_id == movie_id).scalar()
        return float(result) if result else None

    @staticmethod
    def get_rating_count(db: Session, movie_id: int) -> int:
        """Get the number of ratings for a movie."""
        return db.query(Rating).filter(Rating.movie_id == movie_id).count()

    @staticmethod
    def create(db: Session, user_id: int, movie_id: int, rating: float, timestamp: int) -> Rating:
        """Create a new rating."""
        new_rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=rating,
            timestamp=timestamp
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating

    @staticmethod
    def update(db: Session, rating: Rating, new_rating: float = None, timestamp: int = None) -> Rating:
        """Update an existing rating."""
        if new_rating is not None:
            rating.rating = new_rating
        if timestamp is not None:
            rating.timestamp = timestamp

        db.commit()
        db.refresh(rating)
        return rating

    @staticmethod
    def delete(db: Session, rating: Rating) -> None:
        """Delete a rating."""
        db.delete(rating)
        db.commit()

    @staticmethod
    def count(db: Session) -> int:
        """Get total count of ratings."""
        return db.query(Rating).count()

