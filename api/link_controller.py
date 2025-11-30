from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import LinkDAO
from api.dto import LinkResponse, LinkCreate, LinkUpdate
from security import verify_token

router = APIRouter(tags=["Links"])


@router.get("/links", response_model=List[LinkResponse])
def get_links(
    limit: int = Query(None, ge=1),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get all links with optional limit."""
    if limit:
        links_list = LinkDAO.get_all(db, skip=0, limit=limit)
    else:
        links_list = LinkDAO.get_all(db, skip=0, limit=1000000)
    return links_list


@router.get("/links/{movie_id}", response_model=LinkResponse)
def get_link(
    movie_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get a specific link by movie ID."""
    link = LinkDAO.get_by_movie_id(db, movie_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.post("/links", response_model=LinkResponse, status_code=201)
def create_link(
    link_data: LinkCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Create a new link."""
    existing_link = LinkDAO.get_by_movie_id(db, link_data.movie_id)
    if existing_link:
        raise HTTPException(status_code=400, detail="Link for this movie already exists")

    new_link = LinkDAO.create(
        db=db,
        movie_id=link_data.movie_id,
        imdb_id=link_data.imdb_id,
        tmdb_id=link_data.tmdb_id
    )
    return new_link


@router.put("/links/{movie_id}", response_model=LinkResponse)
def update_link(
    movie_id: int,
    link_data: LinkUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Update an existing link."""
    link = LinkDAO.get_by_movie_id(db, movie_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    updated_link = LinkDAO.update(
        db=db,
        link=link,
        imdb_id=link_data.imdb_id,
        tmdb_id=link_data.tmdb_id
    )
    return updated_link


@router.delete("/links/{movie_id}", status_code=204)
def delete_link(
    movie_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Delete a link."""
    link = LinkDAO.get_by_movie_id(db, movie_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    LinkDAO.delete(db, link)
    return None
