from fastapi import APIRouter, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import MovieDAO
from pydantic import BaseModel


class MovieResponse(BaseModel):
    movie_id: int
    title: str
    genres: str

    class Config:
        from_attributes = True


router = APIRouter(tags=["Movies"])


@router.get("/movies", response_model=List[MovieResponse])
def get_movies(limit: int = Query(None, ge=1), db: Session = Depends(get_db)):
    """Get all movies with optional limit."""
    if limit:
        movies_list = MovieDAO.get_all(db, skip=0, limit=limit)
    else:
        movies_list = MovieDAO.get_all(db, skip=0, limit=1000000)
    return movies_list

