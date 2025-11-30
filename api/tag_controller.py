from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import TagDAO
from api.dto import TagResponse, TagCreate, TagUpdate
from security import verify_token

router = APIRouter(tags=["Tags"])


@router.get("/tags", response_model=List[TagResponse])
def get_tags(
    limit: int = Query(1000, ge=1, le=1_000_000),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get all tags with limit."""
    tags_list = TagDAO.get_all(db, skip=0, limit=limit)
    return tags_list


@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Get a specific tag by ID."""
    tag = TagDAO.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Create a new tag."""
    new_tag = TagDAO.create(
        db=db,
        user_id=tag_data.user_id,
        movie_id=tag_data.movie_id,
        tag=tag_data.tag,
        timestamp=tag_data.timestamp
    )
    return new_tag


@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Update an existing tag."""
    tag = TagDAO.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    updated_tag = TagDAO.update(
        db=db,
        tag_obj=tag,
        tag=tag_data.tag,
        timestamp=tag_data.timestamp
    )
    return updated_tag


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    """Delete a tag."""
    tag = TagDAO.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    TagDAO.delete(db, tag)
    return None
