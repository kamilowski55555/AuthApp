from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import MovieDAO
from api.dto import MovieResponse, MovieCreate, MovieUpdate
from security import verify_token

router = APIRouter(tags=["Movies"])


@router.get("/movies", response_model=List[MovieResponse])
def get_movies(
    limit: int = Query(None, ge=1),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get all movies with optional limit."""
    if limit:
        movies_list = MovieDAO.get_all(db, skip=0, limit=limit)
    else:
        movies_list = MovieDAO.get_all(db, skip=0, limit=1000000)
    return movies_list


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get a specific movie by ID."""
    movie = MovieDAO.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/movies", response_model=MovieResponse, status_code=201)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Create a new movie."""
    existing_movie = MovieDAO.get_by_id(db, movie_data.movie_id)
    if existing_movie:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")

    new_movie = MovieDAO.create(
        db=db,
        movie_id=movie_data.movie_id,
        title=movie_data.title,
        genres=movie_data.genres
    )
    return new_movie


@router.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Update an existing movie."""
    movie = MovieDAO.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    updated_movie = MovieDAO.update(
        db=db,
        movie=movie,
        title=movie_data.title,
        genres=movie_data.genres
    )
    return updated_movie


@router.delete("/movies/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Delete a movie."""
    movie = MovieDAO.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    MovieDAO.delete(db, movie)
    return None
