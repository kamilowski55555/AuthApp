from sqlalchemy.orm import Session
from model.movie import Movie
from typing import Optional, List


class MovieDAO:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
        """Get all movies with pagination."""
        return db.query(Movie).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        """Get a movie by its ID."""
        return db.query(Movie).filter(Movie.movie_id == movie_id).first()

    @staticmethod
    def get_by_title(db: Session, title: str) -> Optional[Movie]:
        """Get a movie by exact title."""
        return db.query(Movie).filter(Movie.title == title).first()

    @staticmethod
    def search_by_title(db: Session, title: str, limit: int = 20) -> List[Movie]:
        """Search movies by partial title match."""
        return db.query(Movie).filter(Movie.title.like(f"%{title}%")).limit(limit).all()

    @staticmethod
    def get_by_genre(db: Session, genre: str, limit: int = 50) -> List[Movie]:
        """Get movies by genre."""
        return db.query(Movie).filter(Movie.genres.like(f"%{genre}%")).limit(limit).all()

    @staticmethod
    def create(db: Session, movie_id: int, title: str, genres: str) -> Movie:
        """Create a new movie."""
        new_movie = Movie(
            movie_id=movie_id,
            title=title,
            genres=genres
        )
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        return new_movie

    @staticmethod
    def update(db: Session, movie: Movie, title: str = None, genres: str = None) -> Movie:
        """Update an existing movie."""
        if title is not None:
            movie.title = title
        if genres is not None:
            movie.genres = genres

        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def delete(db: Session, movie: Movie) -> None:
        """Delete a movie."""
        db.delete(movie)
        db.commit()

    @staticmethod
    def count(db: Session) -> int:
        """Get total count of movies."""
        return db.query(Movie).count()