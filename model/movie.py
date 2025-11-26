from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    genres = Column(String, nullable=False, default="")

    link = relationship("Link", back_populates="movie", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Movie(movie_id={self.movie_id}, title='{self.title}')>"
