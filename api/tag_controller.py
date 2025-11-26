from fastapi import APIRouter, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from dao import TagDAO
from pydantic import BaseModel


class TagResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    tag: str
    timestamp: int

    class Config:
        from_attributes = True


router = APIRouter(tags=["Tags"])


@router.get("/tags", response_model=List[TagResponse])
def get_tags(limit: int = Query(1000, ge=1, le=1_000_000), db: Session = Depends(get_db)):
    """Get all tags with limit."""
    tags_list = TagDAO.get_all(db, skip=0, limit=limit)
    return tags_list

