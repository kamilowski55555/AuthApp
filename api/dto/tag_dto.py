from pydantic import BaseModel, Field
from typing import Optional


class TagResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    tag: str
    timestamp: int

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    user_id: int = Field(..., description="User ID")
    movie_id: int = Field(..., description="Movie ID")
    tag: str = Field(..., min_length=1, description="Tag text")
    timestamp: int = Field(..., description="Unix timestamp")


class TagUpdate(BaseModel):
    tag: Optional[str] = Field(None, min_length=1, description="Tag text")
    timestamp: Optional[int] = Field(None, description="Unix timestamp")
