from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from db.database import get_db
from dao import LinkDAO
from pydantic import BaseModel


class LinkResponse(BaseModel):
    movie_id: int
    imdb_id: str
    tmdb_id: Optional[str]

    class Config:
        from_attributes = True


router = APIRouter(tags=["Links"])


@router.get("/links", response_model=List[LinkResponse])
def get_links(limit: int = Query(None, ge=1), db: Session = Depends(get_db)):
    """Get all links with optional limit."""
    if limit:
        links_list = LinkDAO.get_all(db, skip=0, limit=limit)
    else:
        links_list = LinkDAO.get_all(db, skip=0, limit=1000000)
    return links_list

