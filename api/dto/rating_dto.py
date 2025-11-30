from pydantic import BaseModel, Field
from typing import Optional


class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    timestamp: int

    class Config:
        from_attributes = True


class RatingCreate(BaseModel):
    user_id: int = Field(..., description="User ID")
    movie_id: int = Field(..., description="Movie ID")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating value (0.5 to 5.0)")
    timestamp: int = Field(..., description="Unix timestamp")


class RatingUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0.5, le=5.0, description="Rating value (0.5 to 5.0)")
    timestamp: Optional[int] = Field(None, description="Unix timestamp")

