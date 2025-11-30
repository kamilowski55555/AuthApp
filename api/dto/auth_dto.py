from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class LoginData(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    roles: List[str] = Field(default_factory=list)


class UserJWTResponse(BaseModel):
    username: str
    roles: List[str]
    iat: datetime
    exp: datetime

