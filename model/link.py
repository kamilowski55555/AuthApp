from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class Link(Base):
    __tablename__ = "links"

    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True)
    imdb_id = Column(String, nullable=False)
    tmdb_id = Column(String, nullable=True)

    movie = relationship("Movie", back_populates="link")

    def __repr__(self):
        return f"<Link(movie_id={self.movie_id}, imdb_id='{self.imdb_id}')>"
