from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from db.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_ratings_user_movie", "user_id", "movie_id"),
    )

    def __repr__(self):
        return f"<Rating(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"
