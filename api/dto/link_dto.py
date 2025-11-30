from pydantic import BaseModel, Field
from typing import Optional


class LinkResponse(BaseModel):
    movie_id: int
    imdb_id: str
    tmdb_id: Optional[str]

    class Config:
        from_attributes = True


class LinkCreate(BaseModel):
    movie_id: int = Field(..., description="Movie ID")
    imdb_id: str = Field(..., min_length=1, description="IMDb ID")
    tmdb_id: Optional[str] = Field(None, description="TMDb ID")


class LinkUpdate(BaseModel):
    imdb_id: Optional[str] = Field(None, min_length=1, description="IMDb ID")
    tmdb_id: Optional[str] = Field(None, description="TMDb ID")

