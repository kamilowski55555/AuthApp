from fastapi import APIRouter, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import RatingDAO
from pydantic import BaseModel


class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    timestamp: int

    class Config:
        from_attributes = True


router = APIRouter(tags=["Ratings"])


@router.get("/ratings", response_model=List[RatingResponse])
def get_ratings(limit: int = Query(1000, ge=1, le=1_000_000), db: Session = Depends(get_db)):
    """Get all ratings with limit."""
    ratings_list = RatingDAO.get_all(db, skip=0, limit=limit)
    return ratings_list

