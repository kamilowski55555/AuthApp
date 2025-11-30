from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import RatingDAO
from api.dto import RatingResponse, RatingCreate, RatingUpdate
from security import verify_token

router = APIRouter(tags=["Ratings"])


@router.get("/ratings", response_model=List[RatingResponse])
def get_ratings(
    limit: int = Query(1000, ge=1, le=1_000_000),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get all ratings with limit."""
    ratings_list = RatingDAO.get_all(db, skip=0, limit=limit)
    return ratings_list


@router.get("/ratings/{rating_id}", response_model=RatingResponse)
def get_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get a specific rating by ID."""
    rating = RatingDAO.get_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@router.post("/ratings", response_model=RatingResponse, status_code=201)
def create_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Create a new rating."""
    new_rating = RatingDAO.create(
        db=db,
        user_id=rating_data.user_id,
        movie_id=rating_data.movie_id,
        rating=rating_data.rating,
        timestamp=rating_data.timestamp
    )
    return new_rating


@router.put("/ratings/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_data: RatingUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Update an existing rating."""
    rating = RatingDAO.get_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    updated_rating = RatingDAO.update(
        db=db,
        rating=rating,
        new_rating=rating_data.rating,
        timestamp=rating_data.timestamp
    )
    return updated_rating


@router.delete("/ratings/{rating_id}", status_code=204)
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Delete a rating."""
    rating = RatingDAO.get_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    RatingDAO.delete(db, rating)
    return None
