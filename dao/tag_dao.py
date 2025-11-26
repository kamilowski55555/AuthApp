from sqlalchemy.orm import Session
from model.tag import Tag
from typing import Optional, List
from sqlalchemy import func


class TagDAO:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags with pagination."""
        return db.query(Tag).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, tag_id: int) -> Optional[Tag]:
        """Get a tag by its ID."""
        return db.query(Tag).filter(Tag.id == tag_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags by a specific user."""
        return db.query(Tag).filter(Tag.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_movie_id(db: Session, movie_id: int, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags for a specific movie."""
        return db.query(Tag).filter(Tag.movie_id == movie_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_tag_name(db: Session, tag: str, limit: int = 50) -> List[Tag]:
        """Get all entries with a specific tag."""
        return db.query(Tag).filter(Tag.tag == tag).limit(limit).all()

    @staticmethod
    def search_tags(db: Session, tag_pattern: str, limit: int = 50) -> List[Tag]:
        """Search tags by partial match."""
        return db.query(Tag).filter(Tag.tag.like(f"%{tag_pattern}%")).limit(limit).all()

    @staticmethod
    def get_popular_tags(db: Session, limit: int = 20) -> List[tuple]:
        """Get most popular tags with their counts."""
        return db.query(
            Tag.tag,
            func.count(Tag.id).label('count')
        ).group_by(Tag.tag).order_by(func.count(Tag.id).desc()).limit(limit).all()

    @staticmethod
    def create(db: Session, user_id: int, movie_id: int, tag: str, timestamp: int) -> Tag:
        """Create a new tag."""
        new_tag = Tag(
            user_id=user_id,
            movie_id=movie_id,
            tag=tag,
            timestamp=timestamp
        )
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag

    @staticmethod
    def update(db: Session, tag_obj: Tag, tag: str = None, timestamp: int = None) -> Tag:
        """Update an existing tag."""
        if tag is not None:
            tag_obj.tag = tag
        if timestamp is not None:
            tag_obj.timestamp = timestamp

        db.commit()
        db.refresh(tag_obj)
        return tag_obj

    @staticmethod
    def delete(db: Session, tag: Tag) -> None:
        """Delete a tag."""
        db.delete(tag)
        db.commit()

    @staticmethod
    def count(db: Session) -> int:
        """Get total count of tags."""
        return db.query(Tag).count()


