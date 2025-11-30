from pydantic import BaseModel, Field
from typing import Optional


class MovieResponse(BaseModel):
    movie_id: int
    title: str
    genres: str

    class Config:
        from_attributes = True


class MovieCreate(BaseModel):
    movie_id: int = Field(..., description="Unique movie ID")
    title: str = Field(..., min_length=1, description="Movie title")
    genres: str = Field(default="", description="Pipe-separated genres")


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Movie title")
    genres: Optional[str] = Field(None, description="Pipe-separated genres")

