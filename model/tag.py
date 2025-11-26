from sqlalchemy import Column, Integer, String, ForeignKey, Index
from db.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)
    tag = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_tags_user_movie", "user_id", "movie_id"),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id}, tag='{self.tag}')>"
