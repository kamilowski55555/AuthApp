from sqlalchemy.orm import Session
from model.link import Link
from typing import Optional, List


class LinkDAO:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Link]:
        """Get all links with pagination."""
        return db.query(Link).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_movie_id(db: Session, movie_id: int) -> Optional[Link]:
        """Get a link by movie ID."""
        return db.query(Link).filter(Link.movie_id == movie_id).first()

    @staticmethod
    def get_by_imdb_id(db: Session, imdb_id: str) -> Optional[Link]:
        """Get a link by IMDb ID."""
        return db.query(Link).filter(Link.imdb_id == imdb_id).first()

    @staticmethod
    def get_by_tmdb_id(db: Session, tmdb_id: str) -> Optional[Link]:
        """Get a link by TMDb ID."""
        return db.query(Link).filter(Link.tmdb_id == tmdb_id).first()

    @staticmethod
    def create(db: Session, movie_id: int, imdb_id: str, tmdb_id: Optional[str] = None) -> Link:
        """Create a new link."""
        new_link = Link(
            movie_id=movie_id,
            imdb_id=imdb_id,
            tmdb_id=tmdb_id
        )
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        return new_link

    @staticmethod
    def update(db: Session, link: Link, imdb_id: str = None, tmdb_id: str = None) -> Link:
        """Update an existing link."""
        if imdb_id is not None:
            link.imdb_id = imdb_id
        if tmdb_id is not None:
            link.tmdb_id = tmdb_id

        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def delete(db: Session, link: Link) -> None:
        """Delete a link."""
        db.delete(link)
        db.commit()

    @staticmethod
    def count(db: Session) -> int:
        """Get total count of links."""
        return db.query(Link).count()

